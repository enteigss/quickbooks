import requests
from bs4 import BeautifulSoup

url = "https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
else:
    print(f"Failed to access {url}, Status Code: {response.status_code}")
