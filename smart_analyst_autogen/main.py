from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager

from autogen.io import IOWebsockets

from smart_analyst_autogen.tools.bus_func import (get_total_due, get_total_credit_transaction,
                                                  get_total_transaction_for_month, aggregate_expenses, plot_pie_chart,
                                                  function_description_map, get_total_debit_transactions)
from dotenv import load_dotenv
import os

load_dotenv()

model = "gpt-3.5-turbo"
llm_config = {
    "model": model,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "temperature": 0
}


def on_connect(iostream: IOWebsockets) -> None:
    print(f"- on_connect(): Connected to client using IOWebsockers {iostream}", flush=True)
    print(" - on_connect(): Receiving messages from client.", flush=True)

    initial_msg = iostream.input()



    data_analyst_assistant = AssistantAgent(
        name="data_analyst_agent",
        llm_config= llm_config,
        system_message="""You are an helpful AI assistant.
        You can help me with basic data analysis for different financial statements.
           - You will answer using the tools provided
           - Consider Rupee as the currency, so for expense unless specified mention it in Rupees. 
           - Always return the response in structure format.
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
             plot_pie_chart, get_total_debit_transactions]



    for tool in tools:
        print(f"##### {tool.__name__}")
        register_function(
            tool,
            caller=data_analyst_assistant,
            executor=user_proxy,
            name=tool.__name__,
            description=function_description_map.get(f"{tool.__name__}")

        )


    conclusion = AssistantAgent(
        name="conclusion",
        system_message="""You are a helpful assistant.
        Base on the history of the groupchat, answer the original question from User_proxy.
        """,
        llm_config=llm_config,
        human_input_mode="NEVER",  # Never ask for human input.
    )

    print(
        f" - on_connect(): Initiating chat with agent {data_analyst_assistant} using message '{initial_msg}"
    )


    # task1 = """what is my spend across different categories and generate a pie chart"""
    task1 = "what is my total debit and credit amount ? "

    # group_chat = GroupChat(agents=[user_proxy, data_analyst_assistant, bi_analyst_assistant,conclusion], messages=[], max_round=5)
    # manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)


    user_proxy.initiate_chat(data_analyst_assistant,
                             message=initial_msg)

    print(user_proxy.chat_messages)