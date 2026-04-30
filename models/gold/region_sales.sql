with silver as (
    select *
    from {{ ref('silver_orders') }}
)

select
    region,
    sum(sales) as total_sales,
    sum(profit) as total_profit,
    round(100.0 * sum(profit) / nullIf(sum(sales), 0), 2) as profit_margin,
    sum(quantity) as total_quantity
from silver
group by region
order by total_sales desc
