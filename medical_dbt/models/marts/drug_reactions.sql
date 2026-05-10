select
    COUNTRY,
    DRUG,
    REACTION,
    DATE,
    count(*) as report_count
from {{ source('staging', 'CLEAN_OPENFDA') }}
group by COUNTRY, DRUG, REACTION, DATE
