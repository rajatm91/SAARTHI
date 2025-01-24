import json
from autogen import UserProxyAgent, AssistantAgent, register_function, GroupChatManager
from autogen.io import IOWebsockets

from agents.tools import (
    get_total_due,
    get_total_credit_transaction,
    get_total_transaction_for_month,
    aggregate_expenses,
    plot_pie_chart,
    get_total_debit_transactions
)

from dotenv import load_dotenv
import os

load_dotenv()

model = "gpt-3.5-turbo"
llm_config = {
    "model": model,
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "temperature": 0
}

function_description_map = {
    "get_total_due": "Calculates the total amount owed by the user",
    "get_total_credit_transaction": "Calculates the total amount refunded or credited in the statement",
    "get_total_transaction_for_month": "Calculates the total transaction value for a month",
    "aggregate_expenses": "Aggregates the expenses based on the groupby parameter",
    "plot_pie_chart": "Plots a pie chart depicting the distribution of expenses based on either month or description",
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

# def on_connect():
#     print("Connection established!")

# def on_connect(ws):
#     print("Connection established!")
    
#     # Listen for messages from the client
#     async def on_message(message):
#         try:
#             # Parse incoming message (expected to be a JSON object)
#             data = json.loads(message)
#             function_name = data.get("function_name")
#             params = data.get("params", [])
            
#             if function_name:
#                 # Call the function from the agents' tools based on the function name
#                 result = execute_function(function_name, *params)
                
#                 # Send the result back to the client
#                 ws.send(json.dumps({"status": "success", "result": result}))
#             else:
#                 ws.send(json.dumps({"status": "error", "message": "Invalid function name."}))
#         except Exception as e:
#             ws.send(json.dumps({"status": "error", "message": str(e)}))

#     # Attach the message handler
#     ws.on_message = on_message

# def execute_function(function_name: str, *args, **kwargs):
#     if function_name not in function_description_map:
#         raise ValueError(f"Function {function_name} is not supported.")
    
#     function_map = {
#         "get_total_due": get_total_due,
#         "get_total_credit_transaction": get_total_credit_transaction,
#         "get_total_transaction_for_month": get_total_transaction_for_month,
#         "aggregate_expenses": aggregate_expenses,
#         "plot_pie_chart": plot_pie_chart,
#     }

#     func = function_map.get(function_name)
#     if func:
#         return func(*args, **kwargs)
#     else:
#         raise ValueError(f"Function {function_name} not found.")
