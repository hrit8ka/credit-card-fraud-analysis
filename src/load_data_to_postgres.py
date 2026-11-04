
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


# --------------------------------------------------
# 1. File paths and database connection
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "creditcard.csv"

# Connect through the local PostgreSQL socket
DATABASE_URL = "postgresql+psycopg:///fraud_detection"

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 2. Load CSV
# --------------------------------------------------

print("Loading CSV dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Original dataset shape: {df.shape}")


# --------------------------------------------------
# 3. Prepare columns for PostgreSQL
# --------------------------------------------------

df = df[["Time", "Amount", "Class"]].copy()

df = df.rename(columns={
    "Time": "transaction_time",
    "Amount": "amount",
    "Class": "class"
})

print(f"Prepared dataset shape: {df.shape}")


# --------------------------------------------------
# 4. Insert data into PostgreSQL
# --------------------------------------------------

print("Connecting to PostgreSQL...")

with engine.begin() as connection:

    # Clear previous rows so rerunning this script
    # does not create duplicate imports.
    connection.execute(
        text("TRUNCATE TABLE transactions RESTART IDENTITY")
    )

    df.to_sql(
        name="transactions",
        con=connection,
        if_exists="append",
        index=False,
        chunksize=5000
    )


# --------------------------------------------------
# 5. Verify import
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT
                COUNT(*) AS total_transactions,
                SUM(CASE WHEN class = 1 THEN 1 ELSE 0 END)
                    AS fraud_transactions,
                SUM(CASE WHEN class = 0 THEN 1 ELSE 0 END)
                    AS legitimate_transactions
            FROM transactions
        """)
    )

    stats = result.fetchone()

    print("\nImport completed successfully!")
    print(f"Total transactions: {stats[0]:,}")
    print(f"Fraud transactions: {stats[1]:,}")
    print(f"Legitimate transactions: {stats[2]:,}")


engine.dispose()
