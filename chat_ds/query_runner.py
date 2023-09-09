import pandas as pd
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

def run_query(query, snowflake_user, snowflake_password, snowflake_account, snowflake_database, snowflake_schema):
    snowflake_engine = create_engine(URL(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        database=snowflake_database,
        schema=snowflake_schema,
    ))
    snowflake_connection = snowflake_engine.connect()
    df = pd.read_sql(query, snowflake_connection)
    return df