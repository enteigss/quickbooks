from openai import OpenAI
import pandas as pd
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import os
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AIJsonProcessor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def _clean_code(self, code: str) -> str:
        """Remove markdown code blocks and ensure proper data variable reference"""
        # Remove markdown code blocks
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*$', '', code)
        
        code = re.sub(r':\s*false\b', ': False', code)
        code = re.sub(r':\s*true\b', ': True', code)
        code = re.sub(r'=\s*false\b', '= False', code)
        code = re.sub(r'=\s*true\b', '= True', code)

        code = code.strip()
        
        return code
    
    def process_json(self, json_data: Dict[str, Any], query: str) -> pd.DataFrame:
        """
        Process JSON data using GPT to extract relevant information based on the query.
        
        Args:
            json_data: Raw JSON data from QuickBooks
            query: User's natural language query
            
        Returns:
            pandas.DataFrame containing the relevant data
        """
        # Create a prompt that explains the task and includes both the query and JSON
        prompt = self._create_extraction_prompt(json_data, query)
        
        # Get GPT to generate Python code to extract the data
        response = self.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": """You are a data extraction expert. 
                Given a JSON structure and a query, generate Python code that will extract 
                the relevant data and return it as a list of dictionaries that can be 
                converted to a pandas DataFrame. The code should not have a variable
                containing the json. The function should take as input a variable named json_data
                Only return the Python code, no explanations."""},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get the generated code
        extraction_code = self._clean_code(response.choices[0].message.content)
        print("Code:", extraction_code)
        
        try:
            # Execute the generated code with the JSON data
            local_vars = {"json_data": json_data}
            exec(extraction_code, {"pd": pd}, local_vars)
            
            # Convert the extracted data to a DataFrame
            if "result" in local_vars and isinstance(local_vars["result"], list):
                return pd.DataFrame(local_vars["result"])
            else:
                raise ValueError("Generated code did not produce a valid result")
                
        except Exception as e:
            print(f"Error executing generated code: {e}")
            # Fallback: Try a simpler extraction approach
            return self._fallback_extraction(json_data, query)
    
    def _create_extraction_prompt(self, json_data: Dict[str, Any], query: str) -> str:
        # Sample of the JSON structure (to keep the prompt size manageable)
        json_sample = self._create_json_sample(json_data)
        
        return f"""
Given this JSON structure from QuickBooks:
{json_sample}

And this user query:
{query}

Generate Python code that will:
1. Extract the relevant data from the JSON
2. Store it in a list of dictionaries with consistent keys
3. Store the final list in a variable named 'result'

Rules:
1. The code should handle cases where fields might be missing or nested differently.
2. There should be no variable storing the sample json in the final code
3. At the end of the code call the function on the variable named json_data and assign the output to result
"""

    def _create_json_sample(self, json_data: Dict[str, Any]) -> str:
        """Create a representative sample of the JSON structure"""
        # If it's a list of items, take the first item
        if isinstance(json_data.get('QueryResponse'), dict):
            for key, value in json_data['QueryResponse'].items():
                if isinstance(value, list) and value:
                    return json.dumps({
                        'QueryResponse': {
                            key: [value[0]]  # Just the first item
                        }
                    }, indent=2)
        return json.dumps(json_data, indent=2)
    
    def _fallback_extraction(self, json_data: Dict[str, Any], query: str) -> pd.DataFrame:
        """Fallback method for simpler data extraction"""
        # Ask GPT for the most important fields to extract based on the query
        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": "Identify the key fields needed from the JSON based on this query."},
                {"role": "user", "content": f"Query: {query}\nWhat are the essential fields to extract?"}
            ]
        )
        
        fields = response.choices[0].message.content.split(',')
        fields = [f.strip() for f in fields]
        
        # Extract just those fields at their top level
        data = []
        if 'QueryResponse' in json_data:
            for entity_type, entities in json_data['QueryResponse'].items():
                if isinstance(entities, list):
                    for entity in entities:
                        row = {}
                        for field in fields:
                            row[field] = entity.get(field, None)
                        data.append(row)
        
        return pd.DataFrame(data)

# Example usage:
"""
processor = AIJsonProcessor(api_key='your-api-key')

# Example query
query = "Show me all billable expenses with their amounts and customers"

# Process the JSON data
df = processor.process_json(quickbooks_json_data, query)
"""