-- in dbt/Arial/tests/generic/test_is_within_reasonable_range.sql

{% test is_within_reasonable_range(model, column_name, min_value, max_value) %}

select
    {{ column_name }}
from {{ model }}
where
    {{ column_name }} < {{ min_value }}
    or {{ column_name }} > {{ max_value }}

{% endtest %}