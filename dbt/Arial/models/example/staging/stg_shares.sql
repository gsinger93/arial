SELECT 
  CAST(price_date AS DATE) AS share_date, 
  open AS open_price, 
  high AS high_price, 
  low AS low_price, 
  close AS close_price, 
  volume AS trading_volume, 
  symbol 
FROM 
  `gs-arial.financial_data_landing.stock_values` 
WHERE 
  symbol IS NOT NULL 
  qualify row_number() over (
    partition by price_date, symbol 
    order by ingest_dateTime desc
  ) = 1 -- This line ensures we only keep the most recent record for each symbol on each date.
