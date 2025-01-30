from typing import Annotated, Literal
from pandas import DataFrame
import pandas as pd
import os
import uuid
import plotly.express as px


def categorize_spend(df: pd.DataFrame) -> pd.DataFrame:
    # Define categories and keywords (substring-based matching)
    category_mapping = {
        "utilities": ["vodafone", "airtel", "bescom"],
        "quick commerce": ["blinkit", "swiggy instamart"],
        "restaurant": ["zomato", "swiggy dineout"],
        "travel": ["makemytrip", "easemytrip"],
        "electronics": ["croma", "reliance digital", "pai electronic"],
        "ecommerce": ["amazon", "myntra", "tata cliq"],
        "rent": ["rent"],
        "grocery": ["kirana"],
        "account transfer": ["acct trf"],
        "medical": ["onemg"],
        "saving": ["mutual fund"]
    }

    # Function to categorize each transaction
    def assign_category(description):
        description_lower = description.lower()
        for category, keywords in category_mapping.items():
            if any(keyword in description_lower for keyword in keywords):  # Substring check
                return category
        return "others"  # Default category for unmatched transactions

    # Apply categorization
    df["category"] = df["narration"].apply(assign_category)

    return df

def get_month_number(month_name: str) -> int:
    from datetime import datetime
    month_name = month_name.split(" ")[0]
    try:
        month_number = datetime.strptime(month_name.strip(), "%b").month
    except ValueError:
        month_number = datetime.strptime(month_name.strip(), "%B").month
    return month_number


def get_transaction_value(df: pd.DataFrame, transaction_type: Literal["debit","credit", "all" ] = "all" ,
                          col: str = "amount") -> float:
    match transaction_type:
        case "debit":
            d_transaction = df[df["type"] == "debit"]
            return round(d_transaction[col].sum(),4)
        case "credit":
            c_transaction = df[df["type"] == "credit"]
            return round(c_transaction[col].sum(), 4)
        case "all":
            df["net_amount"] = df.apply(lambda row: row[col] if row["type"] == "credit" else -row[col],
                                        axis=1)
            net_amount = df["net_amount"].sum()
            return round(net_amount, 4)


def convert_month_to_year_month(user_input: str, reference_year: int=2024) -> str:
    """
    Convert a month name or abbreviation to 'YYYY-MM' format.

    Parameters:
        user_input (str): Month name or abbreviation (e.g., 'Dec', 'December').
        reference_year (int, optional): Year to use, defaults to 2024.

    Returns:
        str: Formatted string in 'YYYY-MM' format.
    """
    from datetime import datetime
    try:
        # Parse month name to month number
        month_number = datetime.strptime(user_input, "%b").month  # Handles short names like 'Dec'
    except ValueError:
        try:
            month_number = datetime.strptime(user_input, "%B").month  # Handles full names like 'December'
        except ValueError:
            return None
    return f"{reference_year}-{month_number:02d}"


def plot_charts(df: DataFrame,
               chart_type: Annotated[Literal["pie", "bar"], "Chart type"],
               image_path: str,
               x_axis: str, title: str
               ) -> dict:
    """
    Generates a spending chart (pie or bar) based on expenses grouped by 'description' or 'month'.

    Parameters:
    - group_by (str): "category" for category-wise grouping, "month" for monthly grouping.
    - chart_type (str): "pie" for a pie chart, "bar" for a bar chart.
    - image_path (str): Directory to save the generated chart image.

    Returns:
    - dict: Path of the saved chart image.
    """

    # Generate unique filename
    os.makedirs(image_path, exist_ok=True)
    file_name = f"{uuid.uuid4()}.png"
    file_path = os.path.join(image_path, file_name)
    print(f"File path : {file_path}")
    # Plot chart
    fig = px.pie(df, values="amount", names=x_axis, title=title) if chart_type == "pie" else px.bar(df, x=x_axis, y="amount", title=title)
    print(f"File path2 : {file_path}")
    # Save chart image
    fig.write_image(file_path)
    print(f"File path3 : {file_path}")

    return {"image_path": file_path}