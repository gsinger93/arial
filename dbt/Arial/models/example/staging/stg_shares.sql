-- This line tells dbt to select data from your 'raw_shares' table.
-- We will need to configure this source in a future ticket (ARIAL-15),
-- but for now, we can use a placeholder. Let's assume your raw data
-- is in a source named 'financial_data_source' and a table 'raw_shares'.
-- We will hardcode it for now to get this working.

WITH source AS (
    SELECT * FROM `gs-arial.financial_data_landing.stock_values`
),

renamed AS (

    SELECT
        CAST(price_date AS DATE) AS share_date,
        open AS open_price,
        high AS high_price,
        low AS low_price,
        close AS close_price,
        volume AS trading_volume,
        symbol
    FROM source
    WHERE symbol IS NOT NULL
    qualify row_number() over (partition by price_date, symbol order by ingest_dateTime desc) =1
    -- This line ensures we only keep the most recent record for each symbol on each date.
)

SELECT * FROM renamed