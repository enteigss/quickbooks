import pandas as pd

data = pd.read_csv("billable_lines.csv")

result = data[data['BillableStatus'].str.lower().str.contains('billable', na=False)]

print(result)

