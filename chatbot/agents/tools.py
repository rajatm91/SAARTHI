import pandas as pd
from typing import Literal, Annotated
import uuid
import matplotlib.pyplot as plt
import os

plt.switch_backend('Agg')  # To prevent GUI backend errors in server environments

# Load data
df = pd.read_csv("/Users/shobhitsaxena/Documents/Project/SAARTHI/data/credit_card_transactions.csv")


def get_month_number(month_name: str) -> int:
    from datetime import datetime
    try:
        month_number = datetime.strptime(month_name.strip(), "%b").month
    except ValueError:
        month_number = datetime.strptime(month_name.strip(), "%B").month
    return month_number


def get_total_debit_transactions() -> float:
    d_transactions = df[df["transaction_amount"] > 0]
    return round(d_transactions["transaction_amount"].sum(), 4)


def get_total_due() -> float:
    return round(df["transaction_amount"].sum(), 4)


def get_total_credit_transaction() -> float:
    c_transaction = df[df["transaction_amount"] < 0]
    return round(c_transaction["transaction_amount"].sum(), 4)


def get_total_transaction_for_month(month: Annotated[str, "Month for transaction value to be calculate"]) -> float:
    month_number = get_month_number(month)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    filtered_df = df[df["transaction_date"].dt.month == month_number]
    return round(filtered_df["transaction_amount"].sum(), 2)


def aggregate_expenses(group_by: Annotated[Literal["description", "month"], "Group by category"]) -> dict:
    spend_data = pd.DataFrame()
    if group_by == "description":
        spend_data = df[df["transaction_amount"] > 0].groupby("description")["transaction_amount"].sum()
    elif group_by == "month":
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
        df["month"] = df["transaction_date"].dt.month_name()
        spend_data = df[df["transaction_amount"] > 0].groupby("month")["transaction_amount"].sum()
    spend_data.to_csv("distribute_expenses.csv")
    return spend_data.to_dict()


def plot_pie_chart(group_by: Annotated[Literal["description", "month"], "Group by category"]) -> str:
    if group_by == "description":
        spend_data = df[df["transaction_amount"] > 0].groupby("description")["transaction_amount"].sum()
        title = "Spend by Category"
    elif group_by == "month":
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
        df["month"] = df["transaction_date"].dt.month_name()
        spend_data = df[df["transaction_amount"] > 0].groupby("month")["transaction_amount"].sum()
        title = "Spend by Month"
    random_name = uuid.uuid4()
    file_name = os.path.join("/Users/shobhitsaxena/Downloads/images/", f"{random_name}.png")
    plt.figure(figsize=(8, 8))
    plt.pie(spend_data, labels=spend_data.index, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.savefig(file_name)
    return file_name
