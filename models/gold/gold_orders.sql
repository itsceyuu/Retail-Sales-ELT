with silver as (
    select *
    from {{ ref('silver_orders') }}
)

select
    region,
    toStartOfMonth(order_date) as order_month,
    count(*) as orders,
    sum(sales) as total_sales,
    sum(profit) as total_profit,
    avg(discount) as avg_discount,
    sum(quantity) as total_quantity,
    sum(sales) / nullIf(sum(quantity), 0) as avg_sales_per_item
from silver
group by
    region,
    order_month
order by
    region,
    order_month
