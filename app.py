from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError
from intuitlib.enums import Scopes
from flask import Flask, request, redirect, render_template, send_file, url_for
import requests
import csv
import os
from inputToQuery import inputToEntity, queryDataframe
import pandas as pd
from parseJson import parseJson
from dotenv import load_dotenv
import json

app = Flask(__name__)

load_dotenv()

# REDIRECT_URI = "http://localhost:8000/callback"
REDIRECT_URI = "https://enigmatic-falls-03075-43083390e422.herokuapp.com/callback"
ENVIRONMENT = "sandbox"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_auth_client():
    access_token = os.getenv("ACCESS_TOKEN")
    realm_id = os.getenv("REALM_ID")
    # refresh_token = os.getenv("REFRESH_TOKEN")

    auth_client = AuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        environment=ENVIRONMENT,
        access_token=access_token,
        realm_id=realm_id
    )

    return auth_client

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authenticate')
def authenticate():
    # Redirect to Intuit authorization URL
    auth_client = get_auth_client()
    authorization_url = auth_client.get_authorization_url([
        Scopes.ACCOUNTING # Specify the scope of the app
    ])

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Handle callback and exchange code for tokens
    try:
        auth_client = get_auth_client()
        # parameters specifying what data app will have access to
        ####
        auth_code = request.args.get('code')
        realm_id = request.args.get('realmId')
        ####

        if not auth_code or not realm_id:
            return "Error: Missing auth_code or realm ID"

        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        os.environ["ACCESS_TOKEN"] = auth_client.access_token
        os.environ["REALM_ID"] = realm_id


        return render_template('authenticate.html')
    except AuthClientError as e:
        print("fail")
        return f"Error during authentication: {e}"

# Make query

@app.route('/nl-query', methods=['GET', 'POST'])
def query_quickbooks():
    try:
        
        # Receive input and extract entity
        input = request.form.get('query') # User inputted query
        query_entity = inputToEntity(input)

        # If demo mode on use pre-saved jsons
        if request.args.get("demo") == "true":

            json_file = ""
            if query_entity == "Bill":
                json_file = "bills.json"
            elif query_entity == "Purchase":
                json_file = "expenses.json"
            else: 
                return "Error: Failed to extract entity"
            
            file_path = os.path.join(os.getcwd(), "sandboxJsons", json_file)
            if not os.path.exists(file_path):
                return f"Error: File {file_path} not found."
            
            with open(file_path, "r") as file:
                data = json.load(file)

            df = parseJson(data, query_entity)
            df = queryDataframe(input, df)
            df.to_csv('query_results.csv', index=False)
            table_html = df.to_html(classes='table table-striped', index=False)

            return render_template('table.html', table=table_html)
        # Else continue with auth client
        auth_client = get_auth_client()
        if not auth_client:
            print("Auth client not found")

        access_token = auth_client.access_token
        realm_id = auth_client.realm_id

        if not realm_id or not access_token:
            return "Error: Missing realm ID or access token."

        # Query the database
        base_url = "https://sandbox-quickbooks.api.intuit.com"
        endpoint = f"/v3/company/{realm_id}/query"
        url = base_url + endpoint

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        query = f"SELECT * FROM {query_entity}"
        response = requests.get(url, headers=headers, params={"query": query})
        if response.status_code == 200:
            json_data = response.json()
            df = parseJson(json_data, query_entity)
            df = queryDataframe(input, df)
            df.to_csv('query_results.csv', index=False)
            table_html = df.to_html(classes='table table-striped', index=False)
        else:
            return f"Error: {response.status_code}, {response.json()}"

        return render_template('table.html', table=table_html)
        

    except Exception as e:
        return f"Error during query: {e}"
    
@app.route('/standard-query', methods=['GET', 'POST'])
def standard_query():
    try:
        auth_client = get_auth_client()
        access_token = auth_client.access_token
        realm_id = auth_client.realm_id

        if not access_token or not realm_id:
            return "Error: Missing access token or realm ID. Please authenticate first."

        # Query the database
        base_url = "https://sandbox-quickbooks.api.intuit.com"
        endpoint = f"/v3/company/{realm_id}/query"
        url = base_url + endpoint

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        purchase_query = "SELECT * FROM Purchase"
        response = requests.get(url, headers=headers, params={"query": purchase_query})
        
        if response.status_code == 200:
            purchases = response.json()['QueryResponse'].get('Purchase', [])
            if purchases == None:
                return "Failed to retrieve Purchases"
            billable_lines = []
            
            for purchase in purchases:
                for line in purchase.get('Line', []):
                    if line == None:
                        return "Failed to retrieve line"

                    details = line.get('AccountBasedExpenseLineDetail', {})
                    if details == {}:
                        details = line.get('ItemBasedExpenseLineDetail', {})
                    if details == {}:
                        return "Failed to retrieve details"

                    if details.get('BillableStatus') == 'Billable':

                        billable_lines.append({
                            'Expense/Bill': 'Expense',
                            'Payee/Vendor': purchase.get('EntityRef', {}).get('name', 'Info Not Available'),
                            'Customer': details.get('CustomerRef', {}).get('name', 'Info Not Available'),
                            'Amount': line.get('Amount'),
                            'Date': purchase.get('TxnDate', 'Info Not Available'),
                            'BillableStatus': details.get('BillableStatus', 'Info Not Available')
                        })

        else:
            return f"Error: {response.status_code}, {response.json()}"

        bill_query = "SELECT * FROM Bill"
        response = requests.get(url, headers=headers, params={"query": bill_query})

        if response.status_code == 200:
            bills = response.json()['QueryResponse'].get('Bill', [])
            if bills == None:
                return "Failed to retrieve Bills"
            
            for bill in bills:
                for line in bill.get('Line', []):
                    if line == None:
                        return "Failed to retrieve line"
                    
                    details = line.get('AccountBasedExpenseLineDetail', {})
                    if details == {}:
                        details = line.get('ItemBasedExpenseLineDetail', {})
                    if details == {}:
                        return "Failed to retrieve details"
                    
                    if details.get('BillableStatus') == 'Billable':

                        billable_lines.append({
                            'Expense/Bill': 'Bill',
                            'Payee/Vendor': bill.get('VendorRef').get('name', "Info Not Available"),
                            'Customer': details.get('CustomerRef', {}).get('name', 'Info Not Available'),
                            'Amount': line.get('Amount'),
                            'Date': bill.get('TxnDate', 'Info Not Available'),
                            'BillableStatus': details.get('BillableStatus', 'Info Not Available'),
                        })

        else:
            return f"Error: {response.status_Code}, {response.json()}"

        csv_file = 'transactions.csv'
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Expense/Bill', 'Payee/Vendor', 'Customer', 'Amount', 'Date', 'BillableStatus'])
            writer.writeheader()
            writer.writerows(billable_lines)

            print(f"Billable lines have been saved to {csv_file}")

        return render_template('query.html', csv_file=csv_file, billable_lines=billable_lines)

    except Exception as e:
        return f"Error during query: {e}"
    
    
@app.route('/download')
def download():
    csv_file = 'billable_lines.csv'
    if os.path.exists(csv_file):
        return send_file(csv_file, as_attachment=True)
    else:
        return "No CSV file found. Run a query first."
    
@app.route('/download-nl')
def downloadNl():
    type = request.args.get('type', 'query')
    folder_path = 'transactions'
    if type == 'query':
        csv_file = 'query_results.csv'
    elif type == 'expenses':
        csv_file = os.path.join(folder_path, 'expenses.xls')
    elif type == 'bills':
        csv_file = os.path.join(folder_path, 'bills.xls')
    else:
        return "Error: invalid table"
    if os.path.exists(csv_file):
        return send_file(csv_file, as_attachment=True)
    else:
        return "No CSV file found."
    
@app.route('/demo')
def demo():
    return render_template('demo.html')

if __name__ == "__main__":
    app.run(port=8000)


