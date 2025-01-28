import json
import pprint
from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager, GroupChat
from autogen.io import IOWebsockets
from pydantic import BaseModel

from agents.tools import (
    get_total_due,
    get_total_credit_transaction,
    get_total_transaction_for_month,
    aggregate_expenses,
    plot_chart,
    get_total_debit_transactions,
)

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

function_description_map = {
    "get_total_due": "Calculates the total amount owed by the user",
    "get_total_credit_transaction": "Calculates the total amount refunded or credited in the statement",
    "get_total_transaction_for_month": "Calculates the total transaction value for a month aggregating the debit and credit",
    "aggregate_expenses": "Aggregates the expenses based on the groupby parameter",
    "plot_chart": "Plots a pie or bar chart depicting the distribution of expenses based on either month or description based on user's input",
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
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 1,
            "work_dir": "tasks",
            "use_docker": False
        },
        default_auto_reply="",
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    )

    tools = [get_total_due, get_total_credit_transaction,  get_total_transaction_for_month, aggregate_expenses,
             plot_chart, get_total_debit_transactions]



    for tool in tools:
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

    user_proxy.initiate_chat(data_analyst_assistant,
                             message=initial_msg, summary_method="last_msg")

    # pprint.pprint(user_proxy.chat_messages)

