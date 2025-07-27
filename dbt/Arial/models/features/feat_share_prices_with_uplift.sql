-- in dbt/Arial/models/features/feat_share_prices_with_uplift.sql

with source_data as (
    select
        symbol as ticker,
        share_date,
        close_price
    from {{ ref('stg_shares') }}
)

select
    ticker,
    share_date,
    close_price,

    -- Calculate the price 30 days in the future
    lead(close_price, 30) over (partition by ticker order by share_date) as future_price_30_days,

    -- Calculate the percentage uplift based on that future price
    (lead(close_price, 30) over (partition by ticker order by share_date) - close_price) / close_price * 100 as target_uplift_pct_30_days

from source_data