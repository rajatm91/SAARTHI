import pandas as pd
from typing import Literal, Annotated, TypeVar
import uuid
import matplotlib
import matplotlib.pyplot as plt
import os

from starlette.responses import FileResponse

matplotlib.use('Agg')

DataFrame = TypeVar('pandas.core.frame.DataFrame')

function_description_map = {
    "get_total_due" : "Calculates the total amount owed by the user",
    "get_total_credit_transaction": "Calculates the total amount refunded or credited in the statement",
    "get_total_transaction_for_month": "Calculates the total transaction value for a month",
    "aggregate_expenses": "Aggregated the expenses based on the groupby parameter",
    "plot_pie_chart": "Plots a pie chart depicting the distribution of expenses based on either month or description"
}


df = pd.read_csv("/Users/shobhitsaxena/Documents/Project/SAARTHI/data/credit_card_transactions.csv")

def get_month_number(month_name):
    from datetime import datetime
    try:
        # Parse the string to get the month number
        month_number = datetime.strptime(month_name.strip(), "%b").month
    except ValueError:
        # If not a short month name, try the full month name
        month_number = datetime.strptime(month_name.strip(), "%B").month

    return month_number


def get_total_debit_transactions() -> float:
    """
    Calculate the total debit transactions in the statment for the user
    :return: float
    """
    d_transactions = df[df["transaction_amount"] > 0]
    return round(d_transactions["transaction_amount"].sum(), 4)



def get_total_due() -> float:
    """
    Calculates the total amount owed by the user
    :param df: Dataframe
    :return: float
    """
    return round(df["transaction_amount"].sum(), 4)



def get_total_credit_transaction() -> float:
    """
    Calculates the total amount refunded or credited in the statment
    :param df: Dataframe
    :return: float
    """
    c_transaction = df[df["transaction_amount"] < 0]
    return round(c_transaction["transaction_amount"].sum(), 4)



def get_total_transaction_for_month(month: Annotated[str, "Month for transaction value to be calculate"]) -> float:
    """
    calculates the total transaction value for a month
    :param month: str
    :param df: Dataframe
    :return: float
    """
    month_number = get_month_number(month)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    filtered_df = df[df["transaction_date"].dt.month == month_number]

    return round(filtered_df["transaction_amount"].sum(), 2)



def aggregate_expenses(group_by: Annotated[Literal["description", "month"],
                                "Category based on which grouping can be done. Allowed values description or month"]) -> dict:
    """
    Aggregated the expenses based on the groupby parameter
    :param group_by:
    :return:
    """
    spend_data: DataFrame = pd.DataFrame()
    if group_by == "description":
        spend_data = df[df["transaction_amount"] > 0].groupby("description")["transaction_amount"].sum()
        # title = "Spend by Category"
    elif group_by == "month":
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
        df["month"] = df["transaction_date"].dt.month_name()
        spend_data = df[df["transaction_amount"] > 0].groupby("month")["transaction_amount"].sum()
        # title = "Spend by Month"

    spend_data.to_csv("distribute_expenses.csv")
    return spend_data.to_dict()


def plot_pie_chart(group_by: Annotated[Literal["description", "month"],
                                "Category based on which grouping can be done. Allowed values description or month"]) -> str:
    """
    Plots a pie chart depicting the distribution of expenses based on either month or description
    :param group_by: str can be either description or month
    :param df: Dataframe
    :return:
    """

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

# def plot_pie_chart(sender, recipient, context) -> str:
#     """
#     Plots a pie chart depicting the distribution of expenses based on either month or description
#     :param data: Dataframe
#     :return:
#     """
#     carryover = context.get("carryover","")
#     if isinstance(carryover, list):
#         carryover = carryover[-1]
#
#     try:
#         filename = context.get("workdir", "") + "/distribute_expenses.csv"
#
#     except Exception as e:
#         data = f""
#
#     title = "Pie Chart"
#     sampled_df = pd.DataFrame.from_dict(data)
#     random_name = uuid.uuid4()
#     file_name = os.path.join("/Users/rajatmishra/downloads/images/", f"{random_name}.png")
#     plt.figure(figsize=(8, 8))
#     plt.pie(df, labels=sampled_df.index, autopct='%1.1f%%', startangle=140)
#     plt.title(title)
#     plt.savefig(file_name)
#     return file_name