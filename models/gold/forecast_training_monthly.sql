with silver as (
    select *
    from {{ ref('silver_orders') }}
)
select
    region,
    toYear(order_date)                              as year,
    toMonth(order_date)                             as month,
    sum(sales)                                      as total_sales,
    sum(profit)                                     as total_profit,
    sum(quantity)                                   as total_quantity,
    avg(discount)                                   as avg_discount,
    round(sum(sales) / nullIf(sum(quantity), 0), 2) as avg_sales_per_item
from silver
group by
    region,
    year,
    month
order by
    region,
    year,
    month