
from sqlalchemy import create_engine, text
import pandas as pd

DATABASE_URL = "postgresql+psycopg:///fraud_detection"

engine = create_engine(DATABASE_URL)


def get_transactions():
    query = text("""
        SELECT
            transaction_time AS "Time",
            amount AS "Amount",
            class AS "Class"
        FROM transactions
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df
