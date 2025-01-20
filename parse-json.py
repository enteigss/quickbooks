import pandas as pd





def parseJson(response, entity):
    data = response.json().get('QueryResponse').get(entity)
    if entity == "Bill":
        df = pd.DataFrame(columns=['VendorName', 'Amount', 'DueDate', 'CustomerName', 'BillableStatus', 'TxnDate'])
    if entity == "Purchase":
        df = pd.DataFrame(columns)
    for entity in data:
        for line in entity.get('Line', []):
            if line == None:
                return "Failed to retrieve line"
                    
            details = line.get('AccountBasedExpenseLineDetail', {})
            if details == {}:
                details = line.get('ItemBasedExpenseLineDetail', {})
            if details == {}:
                return "Failed to retrieve details"
                    
            new_row = pd.DataFrame({'VendorName': [entity.get('VendorRef').get('name', 'Unknown')],
                        'Amount': [line.get('Amount')],
                        'DueDate': [entity.get('DueDate', 'Unknown')],
                        'CustomerName': [details.get('CustomerRef', {}).get('name', 'Unknown')],
                        'BillableStatus': [details.get('BillableStatus', 'Unknown')],
                        'TxnDate': [entity.get('TxnDate', 'Unknown')]})
                    
            df = pd.concat([df, new_row], ignore_index=True)