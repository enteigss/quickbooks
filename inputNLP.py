from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from processors.pandas_llm import PandasLLM
import pandas as pd
from dotenv import load_dotenv

#if not os.environ.get("OPENAI_API_KEY"):
#    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


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
    api_key=OPENAI_API_KEY
)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please output in one word what entity to extract from quickbooks API. Entity Options: Bill or Purchase. Keep in mind that expense is synonymous with purchase, but only ever output Bill or Purchase", 
                #CompanyInfo, Customer, Employee, Estimate, Invoice, Item, Payment, ProfitAndLoss, Vendor",
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
    api_key=OPENAI_API_KEY
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




    




