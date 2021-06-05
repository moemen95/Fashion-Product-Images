# Fashion-Product-Images

## Dataloaders
create_n_populate_database.py

This script run to put the data in pandas dataframes processing it then put it in the database.
Assumptions:
  You have installed mysql server and you know your credentials

## Queries
queries_api.py

Contain 3 Functions
Fetch function to fetch query from database we already created.
Store function to store the query results in aws s3 Bucket assumption you know the s3 bucketname and aws-cli installed on your computer
Fetch and store function which integrate the 2 above function

helper_functions.py
Contains function to measure the performance of the database query

## Notebook queries_test.ipynb
Contains the query results
Visualization
Albumenations transformations
Prediction of ML Model