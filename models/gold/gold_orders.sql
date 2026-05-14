with silver as (
    select *
    from {{ ref('silver_orders') }}
)

select
    region,
    category,
    sub_category,
    product_name,

    toStartOfMonth(order_date) as order_month,

    count(*) as orders,

    sum(sales) as total_sales,
    sum(profit) as total_profit,

    round(
        sum(profit) / nullIf(sum(sales), 0),
        4
    ) as profit_margin,

    0.10 as target_margin,

    case
        when (
            sum(profit) / nullIf(sum(sales), 0)
        ) >= 0.10
            then 'Healthy'
        else 'Below Target'
    end as margin_status,

    avg(discount) as avg_discount,

    sum(quantity) as total_quantity,

    round(
        sum(sales) / nullIf(sum(quantity), 0),
        2
    ) as avg_sales_per_item

from silver

group by
    region,
    category,
    sub_category,
    product_name,
    order_month

order by
    order_month,
    total_sales desc