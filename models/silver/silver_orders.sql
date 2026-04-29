with raw as (
    select *
    from {{ source('bronze', 'bronze_orders') }}
)

select
    cast(order_id as Int64) as order_id,
    parseDateTimeBestEffort(order_date) as order_date,
    parseDateTimeBestEffort(ship_date) as ship_date,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    country_region,
    city,
    state_province,
    postal_code,
    region,
    product_id,
    category,
    sub_category,
    product_name,
    cast(replaceAll(replaceAll(sales, '$', ''), ',', '') as Float64) as sales,
    cast(quantity as Int64) as quantity,
    cast(discount as Float64) as discount,
    cast(replaceAll(replaceAll(profit, '$', ''), ',', '') as Float64) as profit
from raw
