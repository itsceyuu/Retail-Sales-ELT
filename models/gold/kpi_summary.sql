with base as (

    select *
    from {{ ref('gold_orders') }}

),

monthly as (

    select
        order_month,

        sum(total_sales) as total_sales,
        sum(total_profit) as total_profit

    from base

    group by order_month

)

select
    order_month,

    total_sales,
    total_profit,

    round(
        total_profit
        / nullIf(total_sales, 0),
        4
    ) as profit_margin,

    lag(total_sales)
        over(order by order_month)
        as previous_sales,

    round(
        (
            total_sales
            - lag(total_sales)
                over(order by order_month)
        )
        /
        nullIf(
            lag(total_sales)
                over(order by order_month),
            0
        ),
        4
    ) as sales_growth,

    case
        when (
            total_profit
            / nullIf(total_sales, 0)
        ) >= 0.10
            then 'Healthy'
        else 'Below Target'
    end as margin_status

from monthly

order by order_month