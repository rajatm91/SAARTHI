import pathlib
import plotly.express as px
import pandas as pd
from typing import Literal, Annotated
from utils.analytical_functions import (
                        categorize_spend,
                        get_month_number,
                        get_transaction_value,
                        plot_charts,
                        convert_month_to_year_month)

import matplotlib.pyplot as plt
import os
import uuid


plt.switch_backend('Agg')  # To prevent GUI backend errors in server environments

file_path = pathlib.Path(__file__).parents[2] / "data" / "fake_account_statement.csv"
image_path = pathlib.Path(__file__).parents[1] / "static" / "images"
# Load data
df = pd.read_csv(file_path)
df = categorize_spend(df)


def get_total_debit_transactions() -> float:
    return get_transaction_value(df, "debit")


def get_closing_balance(month: Annotated[str | None, "Month for transaction value to be calculate"]=None,
                        reference_year: Annotated[int, "calendar year"] = 2024) -> float:
    """
    Compute the closing balance up to a given month.

    Parameters:
        month (str, optional): The target month in 'YYYY-MM' format.
                               If None, returns the closing balance of the last available month.

    Returns:
        float: The closing balance at the end of the specified month.
    """
    _df = df.copy()  # Avoid modifying the original dataframe
    _df["transaction_date"] = pd.to_datetime(_df["transaction_date"])
    _df['month'] = _df['transaction_date'].dt.to_period('M')  # Extract year-month
    _df['amount'] = _df.apply(lambda x: x['amount'] if x['type'] == 'credit' else -x['amount'],
                              axis=1)  # Adjust for debits

    closing_balances = _df.groupby('month')['amount'].sum().cumsum().reset_index()
    closing_balances['month'] = closing_balances['month'].astype(str)  # Convert to string for filtering
    print(f"closing balances : {closing_balances}")

    if month:
        reference_month = convert_month_to_year_month(month, reference_year)
        result = closing_balances.loc[closing_balances['month'] == reference_month, 'amount']
        final_result = result.iloc[0] if not result.empty else None  # Return balance or None if month not found
    else:
        final_result = closing_balances.iloc[-1]['amount']
    print(f"Final : {final_result}")
    return round(final_result,4) # Return balance for the last available month



def get_total_credit_transaction() -> float:
    return get_transaction_value(df, "credit")


def get_total_transaction_for_month(month: Annotated[str, "Month for transaction value to be calculate"],
                                    transaction_type: Annotated[Literal["credit", "debit","net"],
                                    "specify the type of transaction on which aggregation needs to be done"]) -> float:
    month_number = get_month_number(month)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    filtered_df = df[df["transaction_date"].dt.month == month_number]

    return get_transaction_value(filtered_df, transaction_type)


def get_recurring_expenses(min_months=3):
    """
    Identifies recurring expenses and plots a grouped bar chart showing the amount spent per expense in each month.

    Parameters:
    - df (pd.DataFrame): DataFrame containing bank transaction data.
    - min_months (int): Minimum number of months an expense must appear to be considered recurring.

    Returns:
    - List of recurring expense descriptions.
    - A Plotly grouped bar chart showing the monthly expense trends per recurring expense.
    """
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["year_month"] = df["transaction_date"].dt.to_period("M").astype(str)
    debit_df = df[df["type"] == "debit"]
    expense_counts = debit_df.groupby("narration")["year_month"].nunique()
    recurring_expenses = expense_counts[expense_counts >= min_months].index.tolist()
    recurring_df = debit_df[debit_df["narration"].isin(recurring_expenses)]
    expense_trends = recurring_df.groupby(["year_month", "narration"])["amount"].sum().reset_index()

    os.makedirs(image_path, exist_ok=True)
    file_name = f"{uuid.uuid4()}.png"
    file_path = os.path.join(image_path, file_name)
    print(f"File path : {file_path}")

    fig = px.bar(
        expense_trends,
        x="narration",
        y="amount",
        color="year_month",
        barmode="group",
        title="Grouped Bar Chart of Recurring Expenses per Month",
        labels={"narration": "Recurring Expense", "amount": "Amount Spent", "year_month": "Month"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.write_image(file_path)
    return { "expenses" : recurring_expenses, "image" : file_path }


def aggregate_transactions(group_by: Annotated[Literal["category", "month"], "Group by category"],
                           ) -> dict:
    """
    Aggregates expenses either by 'description' or by 'month'.

    Parameters:
    - group_by (str): "description" to group by transaction description, "month" to group by month.
    - month_val : "parameter to see if we can group transaction description for a given month
    Returns:
    - dict: Aggregated expenses as a dictionary.
    """

    # Ensure 'date' is in datetime format
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')


    # Filter only "debit" transactions (expenses)
    expense_df = df[df["type"] == "debit"]


    if group_by == "category":
        # Group by expense category (description)
        spend_data = expense_df.groupby("category")["amount"].sum().reset_index()
    elif group_by == "month":
        # Extract month name for grouping
        expense_df["month"] = expense_df["transaction_date"].dt.month_name()
        spend_data = expense_df.groupby("month")["amount"].sum().reset_index()

    return spend_data.to_dict()



def plot_chart_categories(chart_type: Annotated[Literal["pie", "bar"], "Chart type"] = "bar") -> dict:
    """
    Generates a spending chart (pie or bar) based on the category'.

    Parameters:
    - chart_type (str): "pie" for a pie chart, "bar" for a bar chart.
    - image_path (str): Directory to save the generated chart image.

    Returns:
    - dict: Path of the saved chart image.
    """
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
    expense_df = df[df["type"] == "debit"].copy()
    spend_data = expense_df.groupby("category")["amount"].sum().reset_index()
    x_axis, title = "category", "Spend by Category"
    return plot_charts(spend_data, chart_type, image_path, x_axis, title)


def plot_chart_month(chart_type: Annotated[Literal["pie", "bar"], "Chart type"] = "bar") -> dict:
    """
    Generates a spending chart (pie or bar) based on the category'.

    Parameters:
    - chart_type (str): "pie" for a pie chart, "bar" for a bar chart.
    - image_path (str): Directory to save the generated chart image.

    Returns:
    - dict: Path of the saved chart image.
    """
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    expense_df = df[df["type"] == "debit"]
    print(expense_df)
    expense_df["month"] = expense_df["transaction_date"].dt.month_name()
    print(expense_df)
    spend_data = expense_df.groupby("month")["amount"].sum().reset_index()
    x_axis, title = "month", "Spend by Month"

    return plot_charts(spend_data,chart_type, image_path, x_axis, title)


def plot_chart_narration(filter_category: Annotated[str,
                "category based on which data needs to be filtered"],
               chart_type: Annotated[Literal["pie", "bar"], "Chart type"] = "bar") -> dict:
    """
    Generates a spending chart (pie or bar) based on the category'.

    Parameters:
    - chart_type (str): "pie" for a pie chart, "bar" for a bar chart.
    - image_path (str): Directory to save the generated chart image.

    Returns:
    - dict: Path of the saved chart image.
    """
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors='coerce')
    print(f"df1: {df}")
    expense_df = df[(df["type"] == "debit") & (df["category"] == filter_category)]
    print(f"df2: {df}")
    spend_data = expense_df.groupby("narration")["amount"].sum().reset_index()
    print(f"df3 : {df}")
    x_axis, title = "narration", f"Spend by Description for Category : {filter_category}"


    return plot_charts(spend_data,chart_type, image_path, x_axis, title)


