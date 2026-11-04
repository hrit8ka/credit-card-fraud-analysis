
from sqlalchemy import text

from database import engine
import pandas as pd

def get_kpis(
    selected_classes,
    min_amount,
    max_amount
):
    query = text("""
        SELECT
            COUNT(*) AS total_transactions,

            COUNT(*) FILTER (
                WHERE class = 1
            ) AS fraud_transactions,

            COUNT(*) FILTER (
                WHERE class = 0
            ) AS legitimate_transactions,

            COALESCE(
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE class = 1)
                    / NULLIF(COUNT(*), 0),
                    3
                ),
                0
            ) AS fraud_rate,

            COALESCE(
                SUM(amount) FILTER (WHERE class = 1),
                0
            ) AS fraud_amount

        FROM transactions

        WHERE
            (
                (:include_legitimate AND class = 0)
                OR
                (:include_fraud AND class = 1)
            )
            AND amount >= :min_amount
            AND amount <= :max_amount
    """)

    params = {
        "include_legitimate": 0 in selected_classes,
        "include_fraud": 1 in selected_classes,
        "min_amount": min_amount,
        "max_amount": max_amount
    }

    with engine.connect() as connection:
        result = connection.execute(query, params).mappings().one()

    return dict(result)


def get_amount_segment_analysis(min_amount, max_amount):
    query = text("""
        SELECT
            CASE
                WHEN amount < 25 THEN 'Under $25'
                WHEN amount < 100 THEN '$25–$99.99'
                WHEN amount < 500 THEN '$100–$499.99'
                ELSE '$500 and above'
            END AS amount_segment,

            COUNT(*) AS total_transactions,

            COUNT(*) FILTER (
                WHERE class = 1
            ) AS fraud_transactions,

            COALESCE(
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE class = 1)
                    / NULLIF(COUNT(*), 0),
                    4
                ),
                0
            ) AS fraud_rate

        FROM transactions

        WHERE amount >= :min_amount
          AND amount <= :max_amount

        GROUP BY amount_segment

        ORDER BY MIN(amount)
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "min_amount": min_amount,
                "max_amount": max_amount
            }
        ).mappings().all()

    return pd.DataFrame(result)
