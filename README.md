# QuickBooks Data Fetcher

A flask-based web application that allows users to connect their QuickBooks account and run queries using natural language.

## Introduction

I began working on QuickBooks Data Fetcher to help a family member who frequently uses QuickBooks but gets frustrated 
with it's lack of features. I thought it would be a good project to experiment with and learn. It is still a work in progress, and 
keep in mind that it uses AI to generate query results so may be prone to error. Do not assume that the query results are accurate. 

If you have a QuickBooks account you can connect and the app will be able to access your data (feature still being tested), but if you don't have an account or just want to see a demo of how it works you can use demo mode, which uses predefined data from a sandbox company. After running the query, you can download the xls files for the tables that query is targeting. 

## Features

- Authentication with QuickBooks using OAuth2.

- Natural Language Querying for QuickBooks data

- Quickly access billable transactions

- Simple Web Interface for user interaction

## Installation

Clone repo: git clone https://github.com/enteigss/quickbooks.git

``` sh
git clone https://github.com/enteigss/quickbooks.git
cd quickbooks-app
```

- Install Intuit's OAuth2 Client: pip install intuit-oauth

- Install Flask: pip install flask

- Install pandas: pip install pandas

- Install OpenAI API: pip install openai

- Install langchain_openai: pip install langchain_openai

- Install langchain_core: pip install langchain_core

- Install RestrictedPython: pip install RestrictedPython

- Run application in command line: python quickbooks.py

## Usage

1. Run the Application

2. Authenticate with Quickbooks or use Demo Mode

3. Write and submit a query


## Technologies Used

- Flask (Backend framework)

- QuickBooks API 

- OAuth2 (Authentication)

- Pandas (Data processing)

- HTML/CSS (Frontend templates)

## Contributing

Feel free to fork this repository and submit a pull request with improvements


