from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

class QuickBooksQuery:
    def __init__(self, table, select="*", where=None, order_by=None, start_position=None, max_results=None):
        """
        Initialize a QuickBooks query object.

        :param table: The name of the IntuitEntity (e.g., "Customer", "Invoice").
        :param select: The columns to select, default is "*".
        :param where: The WHERE clause for filtering results.
        :param order_by: The ORDERBY clause for sorting results.
        :param start_position: The starting position for pagination.
        :param max_results: The maximum number of results to retrieve.
        """

        self.table = table
        self.select = select
        self.where = where
        self.order_by = order_by
        self.start_position = start_position
        self.max_results = max_results

    def build_query(self):
        """
        Build the SQL-like query string for the QuickBooks API.

        :return: A string representing the query.
        """

        query = f"SELECT {self.select} FROM {self.table}"

        if self.where:
            query += f" WHERE {self.where}"
        if self.order_by:
            query += f" ORDERBY {self.order_by}"
        if self.start_position:
            query += f" STARTPOSITION {self.start_position}"
        if self.max_results:
            query += f" MAXRESULTS {self.max_results}"

        return query
    
llm = OpenAI(model="text-davinci=003")

prompt = PromptTemplate(
    input_variables=["query"],
    template="""
    You are a financial assistant. Extract the intent and entities from the following query:
    Query: {query}
    Response:
    """
)

query = "Show me invoices for last month."
formatted_prompt = prompt.format(query=query)
response = llm.generate(formatted_prompt)
print(response)


