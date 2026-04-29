with raw as (
    select *
    from {{ source('bronze', 'bronze_orders') }}
)

select
    order_id,
    toDateTime(
        concat(
            arrayElement(splitByString('/', order_date), 3),
            '-',
            lpad(arrayElement(splitByString('/', order_date), 1), 2, '0'),
            '-',
            lpad(arrayElement(splitByString('/', order_date), 2), 2, '0')
        )
    ) as order_date,
    toDateTime(
        concat(
            arrayElement(splitByString('/', ship_date), 3),
            '-',
            lpad(arrayElement(splitByString('/', ship_date), 1), 2, '0'),
            '-',
            lpad(arrayElement(splitByString('/', ship_date), 2), 2, '0')
        )
    ) as ship_date,
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
