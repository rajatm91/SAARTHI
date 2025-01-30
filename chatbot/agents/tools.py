import pathlib
import plotly.express as px
import pandas as pd
from typing import Literal, Annotated
import uuid
import matplotlib.pyplot as plt
import os
import boto3


plt.switch_backend('Agg')  # To prevent GUI backend errors in server environments

file_path = pathlib.Path(__file__).parents[2] / "data" / "credit_card_transactions.csv"
image_path = pathlib.Path(__file__).parents[1] / "static" / "images"
# Load data
df = pd.read_csv(file_path)




def get_month_number(month_name: str) -> int:
    from datetime import datetime
    try:
        month_number = datetime.strptime(month_name.strip(), "%b").month
    except ValueError:
        month_number = datetime.strptime(month_name.strip(), "%B").month
    return month_number


def get_transaction_value(df: pd.DataFrame, transaction_type: Literal["debit","credit", "all" ] = "all",
                          amount: str = "transaction_amount") -> float:
    match transaction_type:
        case "debit":
            d_transaction = df[df[amount] > 0]
            return round(d_transaction[amount].sum(), 4)
        case "credit":
            c_transaction = df[df[amount] < 0]
            return round(c_transaction[amount].sum(), 4)
        case "all":
            return round(df[amount].sum(), 4)

    return round(df[amount].sum(), 4)

def get_total_debit_transactions() -> float:
    return get_transaction_value(df, "debit")


def get_total_due() -> float:
    return get_transaction_value(df, "all")


def get_total_credit_transaction() -> float:
    return get_transaction_value(df, "credit")


def get_closing_balance_for_month(month: Annotated[str, "Month for transaction value to be calculate"],
                                    transaction_type: Annotated[Literal["credit", "debit","net"],
                                    "specify the type of transaction on which aggregation needs to be done"]) -> float:
    month_number = get_month_number(month)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    filtered_df = df[df["transaction_date"].dt.month == month_number]

    return get_transaction_value(filtered_df, transaction_type)


def aggregate_expenses(group_by: Annotated[Literal["description", "month"], "Group by category"]) -> dict:
    spend_data = pd.DataFrame()
    if group_by == "description":
        spend_data = df[df["transaction_amount"] > 0].groupby("description")["transaction_amount"].sum().reset_index()
    elif group_by == "month":
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
        df["month"] = df["transaction_date"].dt.month_name()
        spend_data = df[df["transaction_amount"] > 0].groupby("month")["transaction_amount"].sum().reset_index()
    # spend_data.to_csv("distribute_expenses.csv")
    return spend_data.to_dict()



def plot_chart(group_by: Annotated[Literal["description", "month"], "Group by category"],
                   chart_type: Annotated[Literal["pie", "bar"], "Chart type"] = "bar") -> dict:
    # Assuming df is a predefined DataFrame and image_path is a predefined path

    x_axis = ""
    title = ""
    spend_data = None
    if group_by == "description":
        spend_data = df.groupby("description")["transaction_amount"].sum().reset_index()
        spend_data.columns = ['category', 'total_amount']
        title = "Spend by Category"
        x_axis = 'category'
    elif group_by == "month":
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
        df["month"] = df["transaction_date"].dt.month_name()
        spend_data = df.groupby("month")["transaction_amount"].sum().reset_index()
        spend_data.columns = ['month', 'total_amount']
        title = "Spend by Month"
        x_axis = 'month'

    random_name = uuid.uuid4()
    file_path = os.path.join(image_path, f"{random_name}.png")

    fig = None
    if chart_type == "pie":
        fig = px.pie(spend_data, values='total_amount', names=x_axis, title=title)
    elif chart_type == "bar":
        fig = px.bar(spend_data, x=x_axis, y='total_amount', title=title)

    fig.write_image(file_path)
    #s3_path = upload_image_s3("autogendemo", file_path, f"{random_name}.png",region_name )
    return {"image": file_path}


