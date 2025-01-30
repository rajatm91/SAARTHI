import json
import pprint
from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager, GroupChat
from autogen.io import IOWebsockets
from pydantic import BaseModel

# from agents.tools import (
#     get_total_due,
#     get_total_credit_transaction,
#     get_total_transaction_for_month,
#     aggregate_expenses,
#     plot_chart,
#     get_total_debit_transactions,
# )

from agents.account_statement_tools import (
    get_total_credit_transaction,
    get_total_transaction_for_month,
    get_closing_balance,
    aggregate_transactions,
    plot_chart_narration, plot_chart_categories, plot_chart_month,
    get_total_debit_transactions,
    get_recurring_expenses
)

function_description_map = {
    "get_closing_balance": "Calculates the closing balance a.k.a. net amount in the bank acount ",
    "get_total_credit_transaction": "Calculates the total amount refunded or credited in the statement",
    "get_total_transaction_for_month": "Calculates the total transaction value for a month. Aggregation is done based on user's input. Like `credit` would sum all credit transactions, `debit` would sum debit transactions and `net` would sum both.",
    "aggregate_transactions": "Aggregates the expenses based on the groupby parameter",
    "plot_chart_categories": "Plots a pie or bar chart depicting the distribution of transactions based on category",
    "plot_chart_narration": "Plots a pie or bar chart depicting the distribution of transactions based on narration of a particular category",
    "plot_chart_month": "Plots a pie or bar chart depicting the distribution of transactions based on month",
    "get_recurring_expenses": "Identifies the merchant where we have a recurring expense, basically transactions happening every month"
}

from dotenv import load_dotenv
import os

load_dotenv()



class Steps(BaseModel):
    explanation: str
    output: str


class Reasoning(BaseModel):
    steps: list[Steps]
    final_answer: str


model = "gpt-4o"
llm_config = {
    "model": model,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    # "response_format": Reasoning

}




def on_connect(iostream: IOWebsockets) -> None:
    print(f"- on_connect(): Connected to client using IOWebsockers {iostream}", flush=True)
    print(" - on_connect(): Receiving messages from client.", flush=True)

    initial_msg = iostream.input()

    data_analyst_assistant = AssistantAgent(
        name="data_analyst_agent",
        llm_config=llm_config,
        system_message="""You are an helpful AI assistant.
            You can help me with basic data analysis for different financial statements.
               - You will always answer using the tools provided. If tools are not available then politely mention your capbilities.
               - Consider Rupee as the currency, so for expense unless specified mention it in Rupees.
               - For the charts, ensure that the chart path is returned with message
           Return 'TERMINATE' when the task is done.
            """

    )


    user_proxy = UserProxyAgent(
        name="user_proxy",
        llm_config=False,
        max_consecutive_auto_reply=1,
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 3,
            "work_dir": "tasks",
            "use_docker": False
        },
        default_auto_reply="",
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    )

    # tools = [get_total_due, get_total_credit_transaction,  get_total_transaction_for_month, aggregate_expenses,
    #          plot_chart, get_total_debit_transactions]

    bank_statement_tools = [get_closing_balance, get_total_credit_transaction, get_total_transaction_for_month,
                            aggregate_transactions,plot_chart_narration, plot_chart_month, plot_chart_categories,
                            get_recurring_expenses, get_total_debit_transactions]



    for tool in bank_statement_tools:
        register_function(
            tool,
            caller=data_analyst_assistant,
            executor=user_proxy,
            name=tool.__name__,
            description=function_description_map.get(f"{tool.__name__}")

        )

    # conclusion = AssistantAgent(
    #     name="critic",
    #     system_message="""You are reviewer of the responses,
    #         - Ensure to refine the answers without changing the context.
    #         - Consider Rupee as the currency, so for expense unless specified mention it in Rupees.
    #         - If there are no response from the agent, politely let them know the group's capability,
    #         - Ensure that all details are captured and answer is precise but thorough and complete.
    #         - For answers with images, ensure to send the file path of the image as well.
    #         Return 'TERMINATE' when the task is done.
    #         """,
    #     llm_config=llm_config,
    #     human_input_mode="NEVER",  # Never ask for human input.
    # )

    print(
        f" - on_connect(): Initiating chat with agent {data_analyst_assistant} using message '{initial_msg}"
    )


    # task1 = """what is my spend across different categories and generate a pie chart"""
    #task1 = "what is my total debit and credit amount ?"

   #group_chat = GroupChat(agents=[user_proxy], messages=[], max_round=5)
   #manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    #group_chat = GroupChat(agents=[user_proxy, data_analyst_assistant], messages=[])
    #manager = GroupChatManager(group_chat, llm_config=llm_config)

    initial_msg = "Assuming today is 28th Jan 2025. " + initial_msg

    user_proxy.initiate_chat(data_analyst_assistant,
                             message=initial_msg, summary_method="reflection_with_llm", max_turns=10)

    # pprint.pprint(user_proxy.chat_messages)

