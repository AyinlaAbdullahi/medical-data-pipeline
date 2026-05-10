with hiv as (
    select * from {{ ref('hiv_unified') }}
),

life_expectancy as (
    select * from {{ source('staging', 'CLEAN_WHO_LIFE_EXPECTANCY') }}
)

select
    h.COUNTRY,
    h.YEAR,
    h.hiv_total,
    h.hiv_prevalence,
    h.hiv_new_infections,
    l.VALUE as life_expectancy
from hiv h
left join life_expectancy l on h.COUNTRY = l.COUNTRY and h.YEAR = l.YEAR
