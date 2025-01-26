import pandas as pd

def parseJson(response, query_entity):
    data = response.json().get('QueryResponse').get(query_entity)
    if query_entity == "Bill":
        df = pd.DataFrame(columns=['EntityType','VendorName', 'Amount', 'DueDate', 'CustomerName', 'BillableStatus', 'TxnDate'])
    if query_entity == "Purchase":
        df = pd.DataFrame(columns=['EntityType', 'Name', 'Amount', 'CustomerName', 'BillableStatus', 'TxnDate'])
    for entity in data:
        if entity == None:
            return "Failed to retrieve entity"
        
        for line in entity.get('Line', []):
            if line == None:
                return "Failed to retrieve line"
                    
            details = line.get('AccountBasedExpenseLineDetail', {})
            if details == {}:
                details = line.get('ItemBasedExpenseLineDetail', {})
            if details == {}:
                return "Failed to retrieve details"
                    
            if query_entity == "Bill":
                new_row = pd.DataFrame({'EntityType': 'Bill',
                        'VendorName': [entity.get('VendorRef').get('name', 'Unknown')],
                        'Amount': [line.get('Amount')],
                        'DueDate': [entity.get('DueDate', 'Unknown')],
                        'CustomerName': [details.get('CustomerRef', {}).get('name', 'Unknown')],
                        'BillableStatus': [details.get('BillableStatus', 'Unknown')],
                        'TxnDate': [entity.get('TxnDate', 'Unknown')]})
            elif query_entity == "Purchase":
                new_row = pd.DataFrame({'EntityType': 'Purchase',
                        'Name': [entity.get('EntityRef', {}).get('name', 'Unknown')],
                        'Amount': [line.get('Amount')],
                        'CustomerName': [details.get('CustomerRef', {}).get('name', 'Unknown')],
                        'BillableStatus': [details.get('BillableStatus', 'Unknown')],
                        'TxnDate': [entity.get('TxnDate', 'Unknown')]})
            else:
                print("ERROR: Entity not valid:", query_entity)

            df = pd.concat([df, new_row], ignore_index=True)

            if query_entity == "Bill":
                df['DueDate']  = pd.to_datetime(df['DueDate'])
                df['TxnDate'] = pd.to_datetime(df['TxnDate'])

            elif query_entity == "Purchase":
                df['TxnDate'] = pd.to_datetime(df['TxnDate'])

    return df