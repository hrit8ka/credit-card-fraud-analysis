
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. Project paths and imports
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from database import get_transactions
from analytics import get_kpis, get_amount_segment_analysis


# --------------------------------------------------
# 2. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Credit Card Fraud Analytics",
    page_icon="💳",
    layout="wide"
)


# --------------------------------------------------
# 3. Load data from PostgreSQL
# --------------------------------------------------

@st.cache_data
def load_data():
    return get_transactions()


df = load_data()


# --------------------------------------------------
# 4. Sidebar filters
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")

selected_classes = st.sidebar.multiselect(
    "Transaction Type",
    options=["Legitimate", "Fraud"],
    default=["Legitimate", "Fraud"]
)

class_mapping = {
    "Legitimate": 0,
    "Fraud": 1
}

selected_class_values = [
    class_mapping[label] for label in selected_classes
]

amount_range = st.sidebar.slider(
    "Transaction Amount ($)",
    min_value=0.0,
    max_value=float(df["Amount"].max()),
    value=(0.0, float(df["Amount"].max())),
    step=10.0
)


# --------------------------------------------------
# 5. Apply filters for visualisations
# --------------------------------------------------

filtered_df = df[
    (df["Class"].isin(selected_class_values))
    & (df["Amount"] >= amount_range[0])
    & (df["Amount"] <= amount_range[1])
].copy()


st.sidebar.divider()

st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} transactions"
)


# --------------------------------------------------
# 6. Dashboard header
# --------------------------------------------------

st.title("💳 Credit Card Fraud Analytics")

st.markdown(
    """
    An interactive dashboard for exploring credit card
    transactions, fraud patterns, and transaction risk.
    """
)

st.divider()


# --------------------------------------------------
# 7. Key Performance Indicators (SQL-powered)
# --------------------------------------------------

st.subheader("Key Performance Indicators")

kpis = get_kpis(
    selected_classes=selected_class_values,
    min_amount=amount_range[0],
    max_amount=amount_range[1]
)

total_transactions = int(kpis["total_transactions"])
fraud_transactions = int(kpis["fraud_transactions"])
legitimate_transactions = int(kpis["legitimate_transactions"])
fraud_rate = float(kpis["fraud_rate"])
fraud_amount = float(kpis["fraud_amount"])


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Filtered Transactions",
    f"{total_transactions:,}"
)

col2.metric(
    "Fraud Transactions",
    f"{fraud_transactions:,}"
)

col3.metric(
    "Fraud Rate",
    f"{fraud_rate:.3f}%"
)

col4.metric(
    "Fraud-labelled Amount",
    f"${fraud_amount:,.2f}"
)

st.divider()


# --------------------------------------------------
# 8. Analytics sections
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No transactions match the selected filters. "
        "Please adjust your filters."
    )

else:

    # --------------------------------------------------
    # 8.1 Transaction distribution
    # --------------------------------------------------

    st.subheader("Transaction Distribution")

    distribution = (
        filtered_df["Class"]
        .value_counts()
        .reindex([0, 1], fill_value=0)
        .rename(index={
            0: "Legitimate",
            1: "Fraud"
        })
        .reset_index()
    )

    distribution.columns = [
        "Transaction Type",
        "Count"
    ]

    col1, col2 = st.columns(2)

    with col1:

        fig_distribution = px.pie(
            distribution,
            names="Transaction Type",
            values="Count",
            title="Legitimate vs Fraud Transactions",
            hole=0.45
        )

        st.plotly_chart(
            fig_distribution,
            use_container_width=True
        )

    with col2:

        fig_bar = px.bar(
            distribution,
            x="Transaction Type",
            y="Count",
            title="Transaction Count by Type",
            text="Count"
        )

        fig_bar.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    st.divider()


    # --------------------------------------------------
    # 8.2 Transaction amount analysis
    # --------------------------------------------------

    st.subheader("Transaction Amount Analysis")

    amount_by_class = filtered_df.copy()

    amount_by_class["Transaction Type"] = (
        amount_by_class["Class"]
        .map({
            0: "Legitimate",
            1: "Fraud"
        })
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_box = px.box(
            amount_by_class,
            x="Transaction Type",
            y="Amount",
            color="Transaction Type",
            title="Transaction Amount Distribution",
            points="outliers"
        )

        fig_box.update_yaxes(
            range=[0, 500],
            title="Amount ($)"
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )

        st.caption(
            "The y-axis is limited to $500 to make the "
            "main distribution easier to compare. "
            "Higher-value transactions are not displayed here."
        )

    with col2:

        fig_histogram = px.histogram(
            amount_by_class,
            x="Amount",
            color="Transaction Type",
            nbins=50,
            barmode="overlay",
            opacity=0.65,
            title="Transaction Amount Histogram"
        )

        fig_histogram.update_xaxes(
            range=[0, 500],
            title="Amount ($)"
        )

        st.plotly_chart(
            fig_histogram,
            use_container_width=True
        )

        st.caption(
            "The histogram focuses on transactions up to $500."
        )


    # Amount summary table

    amount_summary = (
        filtered_df
        .groupby("Class")["Amount"]
        .agg(
            Transaction_Count="count",
            Average_Amount="mean",
            Median_Amount="median",
            Maximum_Amount="max",
            Total_Amount="sum"
        )
        .rename(index={
            0: "Legitimate",
            1: "Fraud"
        })
    )

    amount_summary.index.name = "Transaction Type"

    st.markdown("**Transaction Amount Summary**")

    st.dataframe(
        amount_summary.style.format({
            "Average_Amount": "${:,.2f}",
            "Median_Amount": "${:,.2f}",
            "Maximum_Amount": "${:,.2f}",
            "Total_Amount": "${:,.2f}"
        }),
        use_container_width=True
    )


    # --------------------------------------------------
    # 8.3 Fraud rate by transaction amount segment
    # --------------------------------------------------

    st.subheader("Fraud Rate by Transaction Amount Segment")

    if set(selected_class_values) == {0, 1}:

        segment_df = get_amount_segment_analysis(
            min_amount=amount_range[0],
            max_amount=amount_range[1]
        )

        if not segment_df.empty:

            segment_df["fraud_rate"] = pd.to_numeric(
                segment_df["fraud_rate"]
            )

            fig_segments = px.bar(
                segment_df,
                x="amount_segment",
                y="fraud_rate",
                text="fraud_rate",
                hover_data=[
                    "total_transactions",
                    "fraud_transactions"
                ],
                title="Fraud Rate Across Transaction Amount Segments",
                labels={
                    "amount_segment": "Transaction Amount",
                    "fraud_rate": "Fraud Rate (%)",
                    "total_transactions": "Total Transactions",
                    "fraud_transactions": "Fraud Transactions"
                }
            )

            fig_segments.update_traces(
                texttemplate="%{text:.4f}%",
                textposition="outside"
            )

            fig_segments.update_layout(
                yaxis_title="Fraud Rate (%)",
                xaxis_title="Transaction Amount Segment"
            )

            st.plotly_chart(
                fig_segments,
                use_container_width=True
            )

        else:

            st.info(
                "No transactions available for the selected amount range."
            )

    else:

        st.info(
            "Select both Legitimate and Fraud transactions "
            "to compare fraud rates across amount segments."
        )


    st.divider()


    # --------------------------------------------------
    # 8.4 Transaction patterns over elapsed time
    # --------------------------------------------------

    st.subheader("Transaction Patterns Over Time")

    time_df = filtered_df.copy()

    # Time represents seconds elapsed from the first
    # transaction, not an actual clock timestamp.
    time_df["Elapsed Hour"] = (
        time_df["Time"] // 3600
    ).astype(int)

    hourly_transactions = (
        time_df
        .groupby(["Elapsed Hour", "Class"])
        .size()
        .reset_index(name="Transaction Count")
    )

    hourly_transactions["Transaction Type"] = (
        hourly_transactions["Class"]
        .map({
            0: "Legitimate",
            1: "Fraud"
        })
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_hourly_count = px.line(
            hourly_transactions,
            x="Elapsed Hour",
            y="Transaction Count",
            color="Transaction Type",
            markers=True,
            title="Transaction Volume Over Elapsed Hours"
        )

        st.plotly_chart(
            fig_hourly_count,
            use_container_width=True
        )

    with col2:

        hourly_fraud = (
            time_df
            .groupby("Elapsed Hour")
            .agg(
                Total_Transactions=("Class", "count"),
                Fraud_Transactions=("Class", "sum")
            )
            .reset_index()
        )

        hourly_fraud["Fraud Rate (%)"] = (
            hourly_fraud["Fraud_Transactions"]
            / hourly_fraud["Total_Transactions"]
            * 100
        )

        fig_hourly_rate = px.line(
            hourly_fraud,
            x="Elapsed Hour",
            y="Fraud Rate (%)",
            markers=True,
            title="Fraud Rate Over Elapsed Hours"
        )

        st.plotly_chart(
            fig_hourly_rate,
            use_container_width=True
        )

    st.caption(
        "The dataset covers approximately two days. "
        "Elapsed-hour patterns are exploratory and should "
        "not be interpreted as stable recurring time patterns."
    )

    st.divider()


    # --------------------------------------------------
    # 8.5 Transaction explorer
    # --------------------------------------------------

    st.subheader("Transaction Explorer")

    st.markdown(
        "Explore individual transactions matching the selected filters."
    )

    explorer_df = filtered_df.copy()

    explorer_df["Transaction Type"] = (
        explorer_df["Class"]
        .map({
            0: "Legitimate",
            1: "Fraud"
        })
    )

    explorer_df = explorer_df.rename(
        columns={
            "Time": "Elapsed Time (seconds)",
            "Amount": "Amount ($)"
        }
    )

    explorer_df = explorer_df[
        [
            "Elapsed Time (seconds)",
            "Amount ($)",
            "Transaction Type"
        ]
    ]

    st.dataframe(
        explorer_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Displaying {len(explorer_df):,} filtered transactions."
    )


# --------------------------------------------------
# 9. Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Credit Card Fraud Analytics | "
    "Data source: Kaggle Credit Card Fraud Detection Dataset"
)
