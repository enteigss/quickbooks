from openai import OpenAI
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

#if not os.environ.get("OPENAI_API_KEY"):
#    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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"
)

def inputToEntity(userInput):
    """
    userInput - Text input from user (string)
    returns - Entity to query from Quickbooks (string)
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Please output in one world what entity to extract from quickbooks API",
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



messages = [
    (
        "system",
        "Please output in one word what entity to extract from quickbooks API",
    ),
    ("human", "I would like to see all of my Bills"),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)

entity = ai_msg.content
print(type(entity))

output = inputToEntity("I would like to see all of my Bills")
print(output)

