#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Amazon Web services provider implementation to be used by Koku."""
import logging

import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ParamValidationError
from requests.exceptions import ConnectionError as BotoConnectionError
from rest_framework import serializers  # meh

from ..provider_errors import ProviderErrors
from ..provider_interface import ProviderInterface
from api.common import error_obj
from api.models import Provider
from masu.processor import ALLOWED_COMPRESSIONS
from masu.util.aws.common import AwsArn
from masu.util.aws.common import get_cur_report_definitions
from masu.util.aws.common import get_data_exports

LOG = logging.getLogger(__name__)


def _get_sts_access(credentials, region_name=None):
    """Get for sts access."""
    # create an STS client
    arn = None
    error_message = "Unable to assume role with given ARN."
    try:
        arn = AwsArn(credentials)
    except SyntaxError as error:
        LOG.warning(msg=error_message, exc_info=error)
        return {"aws_access_key_id": None, "aws_secret_access_key": None, "aws_session_token": None}

    error_message = f"Unable to assume role with ARN {arn.arn}."
    sts_client = boto3.client("sts", region_name=region_name)
    aws_credentials = {}
    credentials = {}
    try:
        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        assume_role_kwargs = {"RoleArn": arn.arn, "RoleSessionName": "AccountCreationSession"}
        if arn.external_id:
            assume_role_kwargs["ExternalId"] = arn.external_id
        assumed_role = sts_client.assume_role(**assume_role_kwargs)
        aws_credentials = assumed_role.get("Credentials")
    except ParamValidationError as param_error:
        LOG.warning(msg=error_message)
        LOG.info(param_error)
        # We can't use the exc_info here because it will print
        # a traceback that gets picked up by sentry:
        # https://github.com/project-koku/koku/issues/1483
    except (ClientError, BotoConnectionError, NoCredentialsError) as boto_error:
        LOG.warning(msg=error_message, exc_info=boto_error)

    # return a kwargs-friendly format
    return dict(
        aws_access_key_id=aws_credentials.get("AccessKeyId"),
        aws_secret_access_key=aws_credentials.get("SecretAccessKey"),
        aws_session_token=aws_credentials.get("SessionToken"),
    )


def _check_s3_access(bucket, credentials, region_name="us-east-1"):
    """Check for access to s3 bucket."""
    s3_exists = True
    s3_client = boto3.client("s3", region_name=region_name, **credentials)
    try:
        s3_client.head_bucket(Bucket=bucket)
    except (ClientError, BotoConnectionError) as boto_error:
        message = f"Unable to access bucket {bucket} with given credentials."
        LOG.warning(msg=message, exc_info=boto_error)
        s3_exists = False

    return s3_exists


def _check_cost_report_access(credential_name, credentials, bucket=None):
    """Check for provider cost and usage report access."""
    # Cost Usage Reorts service is currently only available in us-east-1
    # https://docs.aws.amazon.com/general/latest/gr/billing.html
    reports = None
    data_export = False

    try:
        # V2 reports use the data-exports client instead of cur
        bcm_client = boto3.client("bcm-data-exports", region_name="us-east-1", **credentials)
        reports = get_data_exports(bcm_client)
        data_export = True
    except (ClientError, BotoConnectionError) as boto_error:
        try:
            cur_client = boto3.client("cur", region_name="us-east-1", **credentials)
            response = get_cur_report_definitions(cur_client)
            reports = response.get("ReportDefinitions", [])
        except (ClientError, BotoConnectionError) as boto_error:
            key = ProviderErrors.AWS_NO_REPORT_FOUND
            message = f"Unable to obtain report data with {credential_name}."
            LOG.warning(msg=message, exc_info=boto_error)
            raise serializers.ValidationError(error_obj(key, message))

    if reports and bucket:
        # filter report definitions to reports with a matching S3 bucket name.
        if data_export:
            bucket_matched = list(
                filter(
                    lambda rep: bucket in rep.get("DestinationConfigurations").get("S3Destination").get("S3Bucket"),
                    reports,
                )
            )
        else:
            bucket_matched = list(filter(lambda rep: bucket in rep.get("S3Bucket"), reports))

        if not bucket_matched:
            key = ProviderErrors.AWS_REPORT_CONFIG
            msg = (
                f"Cost management requires that an AWS Cost and Usage Report is configured for bucket: {str(bucket)}."
            )
            raise serializers.ValidationError(error_obj(key, msg))

        for report in bucket_matched:
            compression_type = (
                report.get("DestinationConfigurations")
                .get("S3Destination")
                .get("S3OutputConfigurations")
                .get("Compression")
                if data_export
                else report.get("Compression")
            )
            if compression_type not in ALLOWED_COMPRESSIONS:
                key = ProviderErrors.AWS_COMPRESSION_REPORT_CONFIG
                internal_msg = (
                    f"{report.get('Compression')} compression is not supported. "
                    f"Reports must use GZIP compression format."
                )
                raise serializers.ValidationError(error_obj(key, internal_msg))
            elements = report.get("AdditionalSchemaElements") if report.get("AdditionalSchemaElements") else []
            if "RESOURCES" not in elements:
                if (
                    not report.get("DataQuery")
                    .get("TableConfigurations")
                    .get("COST_AND_USAGE_REPORT")
                    .get("INCLUDE_RESOURCES")
                ):
                    key = ProviderErrors.AWS_REPORT_CONFIG
                    name = report.get("ReportName") if report.get("ReportName") else report.get("Name")
                    msg = f"Required Resource IDs are not included in report {name}"
                    raise serializers.ValidationError(error_obj(key, msg))
    # Return data_export flag here in case we want to use that for updating a provider
    return data_export


class AWSProvider(ProviderInterface):
    """Provider interface defnition."""

    def name(self):
        """Return name of the provider."""
        return Provider.PROVIDER_AWS

    def cost_usage_source_is_reachable(self, credentials, data_source):
        """Verify that the S3 bucket exists and is reachable."""

        role_arn = credentials.get("role_arn")
        if not role_arn or role_arn.isspace():
            key = ProviderErrors.AWS_MISSING_ROLE_ARN
            message = ProviderErrors.AWS_MISSING_ROLE_ARN_MESSAGE
            raise serializers.ValidationError(error_obj(key, message))

        storage_resource_name = data_source.get("bucket")
        if not storage_resource_name or storage_resource_name.isspace():
            key = ProviderErrors.AWS_BUCKET_MISSING
            message = ProviderErrors.AWS_BUCKET_MISSING_MESSAGE
            raise serializers.ValidationError(error_obj(key, message))

        storage_only = data_source.get("storage_only")
        if storage_only:
            # Limited bucket access without CUR
            return True

        region_kwargs = {}
        if region_name := data_source.get("bucket_region"):
            region_kwargs["region_name"] = region_name

        creds = _get_sts_access(credentials, **region_kwargs)
        # if any values in creds are None, the dict won't be empty
        if bool({k: v for k, v in creds.items() if not v}):
            key = ProviderErrors.AWS_ROLE_ARN_UNREACHABLE
            internal_message = f"Unable to access account resources with ARN {role_arn}."
            raise serializers.ValidationError(error_obj(key, internal_message))

        s3_exists = _check_s3_access(storage_resource_name, creds, **region_kwargs)
        if not s3_exists:
            key = ProviderErrors.AWS_BILLING_SOURCE_NOT_FOUND
            internal_message = f"Bucket {storage_resource_name} could not be found with {role_arn}."
            raise serializers.ValidationError(error_obj(key, internal_message))

        data_export = _check_cost_report_access(role_arn, creds, bucket=storage_resource_name)
        if data_export:
            # TODO Maybe save something back to the provider record for future use during processing.
            # data_export = True
            LOG.info("AWS v2 data export.")

        return True

    def infra_type_implementation(self, provider_uuid, tenant):
        """Return infrastructure type."""
        return None

    def infra_key_list_implementation(self, infrastructure_type, schema_name):
        """Return a list of cluster ids on the given infrastructure type."""
        return []

    def is_file_reachable(self, source, reports_list):
        """Verify that report files are accessible in S3."""
        credentials = source.authentication.credentials
        bucket = source.billing_source.data_source.get("bucket")
        region_name = source.billing_source.data_source.get("bucket_region")
        creds = _get_sts_access(credentials)
        s3_client = boto3.client("s3", region_name=region_name, **creds)
        for report in reports_list:
            try:
                s3_client.get_object(Bucket=bucket, Key=report)
            except ClientError as ex:
                if ex.response["Error"]["Code"] == "NoSuchKey":
                    key = ProviderErrors.AWS_REPORT_NOT_FOUND
                    internal_message = f"File {report} could not be found within bucket {bucket}."
                    raise serializers.ValidationError(error_obj(key, internal_message))
