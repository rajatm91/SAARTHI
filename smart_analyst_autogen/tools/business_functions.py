import copy
import os.path
import uuid
from collections.abc import Callable
from typing import Optional, Union, Any, Literal, Annotated, TypeVar

import pandas as pd
import matplotlib.pyplot as plt
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent, Agent, OpenAIWrapper


DataFrame = TypeVar('pandas.core.frame.DataFrame')


class DataAnalystAgent(ConversableAgent):
    """An agent that acts as a junior data analyst who can perform basic analytical operations like
    reading from csv, groupby, filter and sum over a dataframe"""

    DEFAULT_PROMPT = (
        "You are an helpful AI assistant with access to analytical functions ( via the provided functions). In fact you are the only member you can do slicing and dicing over a dataframe."
    )

    DEFAULT_DESCRIPTION = "A helpful assistant with access to analytical functions. Ask them to perform operation like reading csv, filtering , aggregations."

    def __init__(self,
                 name: str,
                 system_message:Optional[Union[str, list[str]]] = DEFAULT_PROMPT,
                 description: Optional[str] = DEFAULT_DESCRIPTION,
                 is_termination_msg: Optional[Callable[[dict[str, Any]], bool]] = None,
                 max_consecutive_auto_reply: Optional[int] = None,
                 human_input_mode: Literal["ALWAYS","NEVER","TERMINATE"] = "TERMINATE",
                 function_map: Optional[dict[str, Callable]] = None,
                 code_execution_config: Union[dict, Literal[False]] = False,
                 llm_config: Optional[Union[dict, Literal[False]]] = None,
                 default_auto_reply: Optional[Union[str, dict, None]] = "",
                 file_path: Optional[str] = None,
                 **kwargs
                 ):
        super().__init__(
            name=name,
            system_message=system_message,
            description=description,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            function_map=function_map,
            code_execution_config=code_execution_config,
            llm_config=llm_config,
            default_auto_reply=default_auto_reply,
            **kwargs
        )

        inner_llm_config = copy.deepcopy(llm_config)

        self._assistant = AssistantAgent(
            self.name + "_inner_assistant_agent",
            system_message=system_message,
            llm_config=inner_llm_config,
            is_termination_msg= lambda m: False,
        )

        self._user_proxy = UserProxyAgent(
            self.name + "_inner_user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda m: False,
        )

        self.file_path = file_path
        self.df = self.read_transactions()

        if inner_llm_config not in [False, None]:
            self._register_functions()

        self.register_reply([Agent, None], DataAnalystAgent.generate_analysis_reply, remove_other_reply_funcs=True)
        self.register_reply([Agent, None], ConversableAgent.generate_code_execution_reply)
        self.register_reply([Agent, None], ConversableAgent.generate_function_call_reply)
        self.register_reply([Agent, None], ConversableAgent.check_termination_and_human_reply)


    def read_transactions(self):
        """
        A function to read the transactions from a csv file
        :return: pd.Dataframe
        """
        fixed_df = pd.read_csv(self.file_path)
        return fixed_df


    def _register_functions(self) -> None:

        # helper function
        def get_month_number(month_name):
            from datetime import datetime
            try:
                # Parse the string to get the month number
                month_number = datetime.strptime(month_name.strip(), "%b").month
            except ValueError:
                # If not a short month name, try the full month name
                month_number = datetime.strptime(month_name.strip(), "%B").month

            return month_number



        @self._user_proxy.register_for_execution()
        @self._assistant.register_for_llm(
            name="get_total_due",
            description="Calculate the total amount owed based on the transaction data"
        )
        def get_total_due() -> float:
            """
            Calculates the total amount owed by the user
            :param df: Dataframe
            :return: float
            """
            return round(self.df["transaction_amount"].sum(), 4)

        @self._user_proxy.register_for_execution()
        @self._assistant.register_for_llm(
            name="get_total_credit_transaction",
            description="Calculates the total amount refunded or credited based on the transaction data"
        )
        def get_total_credit_transaction() -> float:
            """
            Calculates the total amount refunded or credited in the statment
            :param df: Dataframe
            :return: float
            """
            c_transaction = self.df[self.df["transaction_amount"] < 0]
            return round(c_transaction["transaction_amount"].sum(), 4)

        @self._user_proxy.register_for_execution()
        @self._assistant.register_for_llm(
            name="get_total_credit_transaction",
            description="Calculates the total amount refunded or credited based on the transaction data"
        )
        def get_total_transaction_for_month(month: Annotated[str, "Month for transaction value to be calculate"]) -> float:
            """
            calculates the total transaction value for a month
            :param month: str
            :param df: Dataframe
            :return: float
            """
            month_number = get_month_number(month)
            self.df["transaction_date"] = pd.to_datetime(self.df["transaction_date"])
            filtered_df = self.df[self.df["transaction_date"].dt.month == month_number]

            return round(filtered_df["transaction_amount"].sum(), 2)

        @self._user_proxy.register_for_execution()
        @self._assistant.register_for_llm(
            name="aggregate_expenses",
            description="Analyzes the expense across months or category"
        )
        def aggregate_expenses(group_by: Annotated[Literal["description","month"],
                          "category based on which grouping can be done. Allowed values description or month"]) -> dict:

            spend_data: DataFrame = pd.DataFrame()
            if group_by == "description":
                spend_data = self.df[self.df["transaction_amount"] > 0].groupby("description")["transaction_amount"].sum()
                #title = "Spend by Category"
            elif group_by == "month":
                self.df["transaction_date"] = pd.to_datetime(self.df["transaction_date"], errors='coerce')
                self.df["month"] = self.df["transaction_date"].dt.month_name()
                spend_data = self.df[self.df["transaction_amount"] > 0].groupby("month")["transaction_amount"].sum()
                #title = "Spend by Month"

            print(spend_data)
            print(type(spend_data))
            return spend_data.to_dict()


        @self._user_proxy.register_for_execution()
        @self._assistant.register_for_llm(
            name="plot_pie_chart",
            description="Plots a pie chart depicting the distribution of expenses based on either month or description"
        )
        def plot_pie_chart(data: Annotated[dict, "The dictionary on which the graph is ploted"]) -> str:
            """
            Plots a pie chart depicting the distribution of expenses based on either month or description
            :param group_by: str can be either description or month
            :param df: Dataframe
            :return:
            """

            title = "Pie Chart"
            df = pd.DataFrame.from_dict(data)
            random_name = uuid.uuid4()
            file_name = os.path.join("/Users/rajatmishra/downloads/images/",f"{random_name}.png" )
            plt.figure(figsize=(8, 8))
            plt.pie(df, labels=df.index, autopct='%1.1f%%', startangle=140)
            plt.title(title)
            plt.savefig(file_name)
            return file_name


    def generate_analysis_reply(
            self,
            messages: Optional[list[dict[str,str]]] = None,
            sender: Optional[Agent] = None,
            config: Optional[OpenAIWrapper] = None,
    ) -> tuple[bool, Optional[Union[str, dict[str, str]]]]:

        if messages is None:
            messages = self._oai_messages[sender]

        self._user_proxy.reset()
        self._assistant.reset()

        # clone messages to give context
        self._assistant.chat_messages[self._user_proxy] = list()
        history = messages[0: len(messages) -1]
        for message in history:
            self._assistant.chat_messages[self._user_proxy].append(message)

        self._user_proxy.send(messages[-1]["content"], self._assistant, request_reply=True, silent=False)
        agent_reply = self._user_proxy.chat_messages[self._assistant][-1]

        proxy_reply = self._user_proxy.generate_reply(
            messages=self._user_proxy.chat_messages[self._assistant], sender = self._assistant
        )

        if proxy_reply == "":
            return True, None if agent_reply is None else agent_reply["content"]
        else:
            return True, None if proxy_reply is None else proxy_reply["content"]