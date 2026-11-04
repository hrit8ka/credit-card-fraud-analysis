# Credit Card Fraud Analytics & Detection

An end-to-end data analytics and machine learning project exploring credit card transactions and fraud detection.

The project brings together Python, SQL, PostgreSQL, and machine learning to investigate transaction patterns, understand the characteristics of fraudulent transactions, and build a model to identify potentially fraudulent activity. It also includes an interactive Streamlit dashboard for exploring the data.

## About the project

Credit card fraud detection is an interesting classification problem, particularly because fraudulent transactions make up only a very small proportion of all transactions.

In this project, I wanted to explore how data analysis and machine learning could be used to approach this problem, from understanding the dataset and identifying patterns to building and evaluating a classification model.

The main objectives were to:

- Explore the dataset and understand its characteristics.
- Investigate differences between legitimate and fraudulent transactions.
- Use SQL and PostgreSQL for transaction analysis.
- Build an interactive dashboard to visualise findings.
- Develop a machine learning model for fraud detection.
- Evaluate the model beyond accuracy, with particular attention to precision and recall.

## The dataset
## Dataset

This project uses the Credit Card Fraud Detection dataset from Kaggle.

The dataset is not included in this repository because of its file size.

Download it here:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

After downloading, place `creditcard.csv` inside the `data/` directory.


It contains transactions made by European cardholders over approximately two days in September 2013.

A few key figures:

| Metric | Value |
|---|---:|
| Total transactions | 284,807 |
| Legitimate transactions | 284,315 |
| Fraudulent transactions | 492 |
| Fraud rate | 0.1727% |
| Number of features | 30 |

The dataset includes:

- `Time`: Seconds elapsed since the first transaction in the dataset.
- `Amount`: The transaction amount.
- `V1`–`V28`: Anonymised features obtained through Principal Component Analysis (PCA).
- `Class`: The target variable, where `0` represents a legitimate transaction and `1` represents fraud.

There are no missing values in the dataset. However, duplicate records were identified during the initial investigation, which became an important consideration when designing the model evaluation strategy.

## Tools and technologies

The project uses the following tools:

| Area | Technologies |
|---|---|
| Programming | Python |
| Data manipulation | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Database | PostgreSQL |
| SQL integration | SQLAlchemy, Psycopg |
| Machine learning | Scikit-learn |
| Dashboard | Streamlit |
| Development environment | Jupyter Notebook, VS Code |
| Environment management | uv |

## Exploratory data analysis

I started by looking at the overall transaction distribution, checking data quality, and comparing legitimate and fraudulent transactions.

One of the first things that stands out is the class imbalance: only around 0.17% of transactions are labelled as fraudulent. This has implications for both model development and performance evaluation.

A few observations from the analysis:

**Transaction amounts**

Fraudulent transactions have a higher average amount than legitimate transactions:

- Legitimate transactions: $88.29 on average.
- Fraudulent transactions: $122.21 on average.

However, the median tells a different story. The median fraudulent transaction amount is $9.25, compared with $22.00 for legitimate transactions.

This suggests that a relatively small number of high-value fraudulent transactions influence the average. It also shows why transaction amount alone would not be a reliable way to identify fraud.

**Feature relationships**

Several anonymised features show relatively strong correlations with the fraud label. Among them are `V17`, `V14`, `V12`, and `V10`.

Since these variables have been transformed using PCA, their original financial meaning is not directly available. I therefore focused on understanding their statistical relationships with the target rather than assigning them specific financial interpretations.

**Duplicate records**

Duplicate transactions were also investigated. Rather than relying on a conventional random split, I used a group-aware splitting strategy during model evaluation to reduce the possibility of identical feature records appearing in both training and testing data.

## SQL and PostgreSQL analysis

I incorporated PostgreSQL into the project to make the transaction data available through a structured database rather than relying exclusively on CSV files.

The dataset was loaded into a `transactions` table containing the transaction ID, transaction time, amount, and transaction class.

I then used SQL to investigate several aspects of the data, including:

- Overall transaction volume and fraud distribution.
- Fraud rates across the dataset.
- Average, minimum, and maximum transaction amounts.
- Total transaction value by transaction type.
- Highest-value transactions labelled as fraudulent.
- Fraud rates across different transaction amount segments.

The SQL queries are organised in the `sql/` directory. Python connects to the database through SQLAlchemy and Psycopg.

## Interactive dashboard

To make the analysis easier to explore, I built an interactive dashboard using Streamlit and Plotly.

The dashboard currently includes:

- Key metrics such as transaction volume, fraud count, fraud rate, and fraud-labelled transaction amount.
- Filters for transaction type and transaction amount.
- A comparison of legitimate and fraudulent transactions.
- Transaction amount distributions and histograms.
- Fraud rates across transaction amount segments.
- Transaction patterns over elapsed time.
- A transaction explorer for viewing individual records.

The dashboard retrieves transaction data from PostgreSQL. KPI calculations and fraud rate segmentation are performed directly in SQL, while pandas is used for filtering and preparing the data behind the other visualisations.

## Machine learning approach

For the classification task, I developed a Logistic Regression model using Scikit-learn.

I chose it as a baseline because it provides a relatively straightforward approach to binary classification and offers a useful starting point for evaluating the fraud detection problem.

The modelling pipeline consists of:

1. `StandardScaler` to standardise the input features.
2. `LogisticRegression` with `class_weight="balanced"` to account for the substantial class imbalance.

The original anonymised features were used as predictors, with `Class` as the target variable.

### Handling data leakage

During the initial data investigation, I identified duplicate feature records. This raised the possibility that a conventional random train-test split could place identical records in both sets and produce overly optimistic evaluation results.

To address this, I used `StratifiedGroupKFold` with groups based on the transaction feature records.

The final split contained:

| | Training set | Test set |
|---|---:|---:|
| Transactions | 227,845 | 56,962 |
| Fraud cases | 393 | 99 |

The validation process also used group-aware splitting. The classification threshold was selected using the validation data, keeping the final test set separate from model selection.

### Choosing the classification threshold

Because the dataset is highly imbalanced, the default classification threshold was not necessarily the most suitable choice.

I evaluated different thresholds on the validation set, prioritising fraud recall while maintaining a reasonable level of precision.

The selected threshold was **0.9750**.

### Model evaluation

The final model was evaluated on the untouched test set.

| Metric | Result |
|---|---:|
| Precision | 51.18% |
| Recall | 87.88% |
| F1-score | 64.68% |
| Average Precision | 76.19% |
| ROC-AUC | 97.97% |
| Accuracy | 99.83% |

The confusion matrix was:

| | Predicted legitimate | Predicted fraud |
|---|---:|---:|
| Actual legitimate | 56,780 | 83 |
| Actual fraud | 12 | 87 |

### What do these results mean?

The model identified 87 out of the 99 fraudulent transactions in the test set, while missing 12.

It also incorrectly flagged 83 legitimate transactions as fraudulent.

The recall of 87.88% indicates that the model identified most of the fraudulent transactions in the test set. However, its precision of 51.18% means that approximately half of the transactions flagged by the model were actually fraudulent.

This illustrates an important trade-off in fraud detection: increasing the number of fraudulent transactions identified can also increase the number of false alerts.

In a real-world setting, the appropriate balance would depend on factors such as investigation capacity, customer experience, and the cost of missed fraudulent transactions.

The model's output scores should not be interpreted as calibrated fraud probabilities.

## Limitations and considerations

There are a few limitations worth keeping in mind when interpreting the results:

- The dataset covers only approximately two days, so temporal patterns should be treated as exploratory rather than evidence of recurring behaviour.
- The PCA-transformed features are anonymised, which limits their direct interpretability.
- Fraudulent transactions represent a very small proportion of the dataset.
- The final test set contains 99 fraudulent cases, so individual predictions have a noticeable effect on the reported metrics.
- Fraud-labelled transaction amounts should not be interpreted as confirmed financial losses.
- Logistic Regression provides a useful baseline, but other models and approaches could be investigated.
- The project uses historical data and does not represent a live fraud monitoring system.

## Getting started

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd credit-card-fraud-analysis
```

### 2. Set up the environment

The project uses `uv` for environment management.

```bash
uv venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
uv pip install -r requirements.txt
```

### 3. Set up PostgreSQL

Create the database:

```bash
createdb fraud_detection
```

Connect to it:

```bash
psql fraud_detection
```

Create the transactions table:

```sql
CREATE TABLE transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_time DOUBLE PRECISION NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    class SMALLINT NOT NULL CHECK (class IN (0, 1))
);
```

Exit PostgreSQL using `\q`.

### 4. Download and load the dataset

Download `creditcard.csv` from the Kaggle dataset page and place it inside the `data/` directory.

Run the loading script:

```bash
python src/load_data_to_postgres.py
```

This loads the transaction records into PostgreSQL.

### 5. Launch the dashboard

From the project root, run:

```bash
streamlit run dashboard/app.py
```

The dashboard should open in your browser.

## Possible next steps

There are several directions in which this project could be extended:

- Compare Logistic Regression with Random Forest and other classification algorithms.
- Add model performance metrics and a confusion matrix to the dashboard.
- Explore model calibration and different threshold-selection strategies.
- Use SHAP or other explainability techniques to investigate model predictions.
- Add an interface for testing new transactions.
- Introduce automated testing and data validation.
- Deploy the dashboard.

## Author

Developed as a personal data analytics and machine learning project, bringing together exploratory data analysis, SQL, PostgreSQL, interactive visualisation, and classification modelling.

---

*This project is intended for educational and portfolio purposes. It is not a production-ready financial fraud detection system.*