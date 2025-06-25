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
        -- Let's cast the timestamp to a proper DATE data type
        CAST(price_date AS DATE) AS share_date,

        -- Rename the columns to be more user-friendly and select only what we need
        open AS open_price,
        high AS high_price,
        low AS low_price,
        close AS close_price,
        volume AS trading_volume,

        -- It's good practice to also include the symbol if you have it
        symbol

    FROM source

)

SELECT * FROM renamed