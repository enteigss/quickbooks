from openai import OpenAI
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pandas_llm import PandasLLM
import pandas as pd

#if not os.environ.get("OPENAI_API_KEY"):
#    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

OPENAI_API_KEY = "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"



def inputToEntity(userInput):
    """
    userInput - Text input from user (string)
    returns - Entity to query from Quickbooks (string)
    """

    llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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"
)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please output in one word what entity to extract from quickbooks API. Entity Options: Bill, CompanyInfo, Customer, Employee, Estimate, Invoice, Item, Payment, ProfitAndLoss, Vendor",
            ),
            ("human", "{input}")
        ]
    )

    chain = prompt | llm
    msg = chain.invoke(
        {
            "input": userInput,
        }
    )

    return msg.content

def inputToColumns(userInput):
    """
    userInput - Text input from user (string)
    """

    llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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"
)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please select the columns the user wants. Select one or more columns from: VendorName, Amount, DueDate, CustomerName, BillableStatus, TxnDate",
            ),
            ("human", "{input}")
        ]
    )

    chain = prompt | llm
    msg = chain.invoke(
        {
            "input": userInput,
        }
    )

    return msg.content

def queryDataframe(userInput, df):
    """
    userInput - Text input from user (string)
    """

    conv_df = PandasLLM(data=df, llm_api_key=os.environ.get("OPENAI_API_KEY"))
    result = conv_df.prompt(userInput)
    code = conv_df.code_block
    print(f"Executing the following expression of type {type(result)}:\n{code}\n\nResult is:\n {result}\n")


    




