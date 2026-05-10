with hiv_total as (
    select * from {{ source('staging', 'CLEAN_WHO_HIV_TOTAL') }}
),

hiv_prevalence as (
    select * from {{ source('staging', 'CLEAN_WHO_HIV_PREVALENCE') }}
),

hiv_new_infections as (
    select * from {{ source('staging', 'CLEAN_WHO_HIV_NEW_INFECTIONS') }}
)

select
    t.COUNTRY,
    t.YEAR,
    t.VALUE                 as hiv_total,
    p.VALUE                 as hiv_prevalence,
    n.VALUE                 as hiv_new_infections
from hiv_total t
left join hiv_prevalence p  on t.COUNTRY = p.COUNTRY and t.YEAR = p.YEAR
left join hiv_new_infections n on t.COUNTRY = n.COUNTRY and t.YEAR = n.YEAR
