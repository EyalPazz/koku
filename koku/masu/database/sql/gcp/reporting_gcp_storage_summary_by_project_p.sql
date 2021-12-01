DELETE FROM {{schema | sqlsafe}}.reporting_gcp_storage_summary_by_project_p
WHERE usage_start >= {{start_date}}::date
    AND usage_start <= {{end_date}}::date
    AND source_uuid = {{source_uuid}}
    AND invoice_month = {{invoice_month}}
;

INSERT INTO reporting_gcp_storage_summary_by_project_p (
    id,
    usage_start,
    usage_end,
    usage_amount,
    unit,
    unblended_cost,
    markup_cost,
    currency,
    project_id,
    project_name,
    account_id,
    source_uuid,
    invoice_month,
    credit_amount
)
    SELECT uuid_generate_v4() as id,
        usage_start,
        usage_start as usage_end,
        sum(usage_amount) as usage_amount,
        MAX(unit) AS unit,
        SUM(unblended_cost) AS unblended_cost,
        SUM(markup_cost) AS markup_cost,
        MAX(currency) AS currency,
        project_id,
        project_name,
        account_id,
        max(source_uuid::text)::uuid as source_uuid,
        invoice_month,
        SUM(credit_amount) AS credit_amount
    FROM reporting_gcpcostentrylineitem_daily_summary
    WHERE usage_start >= {{start_date}}::date
        AND usage_start <= {{end_date}}::date
        AND source_uuid = {{source_uuid}}
        AND service_alias IN ('Filestore', 'Storage', 'Cloud Storage', 'Data Transfer')
        AND invoice_month = {{invoice_month}}
    GROUP BY usage_start, project_id, project_name, account_id, invoice_month
;