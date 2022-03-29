# Reward Points Exercise
Simple Flask app that accepts HTTP requests and returns responses based on conditions outlined in the section below. 

## Premise
* Every user has an `accounts` that stores `points` per `payers`.
* Payer submit transactions. 
  * Each transaction should include `payer`, `points`,`timestamp` information.
  * Transactions are not necessarily added in the order of their transaction timestamps. 
  * A transaction will be added to `positiveTransactions` list or `negativeTransactions` list based on positive or negative points involved.
  * Transactions are stored in memory on the back end.
  * A payer's total points can go below 0 in the middle of adding transactions, but it won't be below 0 after adding all transactions.
* The user can `spend` points.
  * The user's total points can't go below 0.
  * When spending points, the oldest points are spent first based on their transaction's timestamp, regardless of payer.

## Usage
1) You must have [python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/getting-started/) installed.    
    
2) Clone repo locally
    ```
    git clone https://github.com/xuxiaqing2011/Reward-Points
    ```
3) Go to the project's root directory
    ```
    cd /my/path/to/Reward-Points
    ```
4) Install packages
    ```
    pip install -r requirements.txt
    ```
5) Start the server
    ```
    python app.py
    ```
   
6) Verify the app is running by visiting http://localhost:5000/. You should see the following greeting:  
    "Home Page"

## Making API calls
**NOTE** Because this web service doesn't use any durable data store, there will be no data in the backend whenever the sever is started, which means:
* The user will initially have a zero balance.
* Accounts, positiveTransactions, negativeTransactions will be empty.

From any curl tool such as Postman or a basic shell curl command, make requests to http://localhost:5000/ENDPOINT where ENDPOINT is one of the routes described below. For POST requests, such as adding a transaction or spending points, use JSON schema.

### Routes
Currently only the following routes are implemented:
1. Show Points: `/check_balance`
    ```
    GET http://localhost:5000/check_balance
    ```
    This route gives the user `accounts` information, which reveals `points` per `payer`.

2. Add points: `/add_transactions`
    ```
    POST http://localhost:5000/add_transactions
    Example JSON: { "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }
    ```

    **NOTE:** Transactions with positive points are added to the `positiveTransaction` and inserted at the right place based on timestamp (later -> early). Transactions with negative points are added to the `negativeTransaction`, these transactions are later used to negate the positive points when a spending call is made. 

3. Spend points: `/spend_points`
    ```
    POST http://localhost:5000/spend_points
    Example JSON: { "points": 5000 }
    ```
    **NOTE:** Spending calls uses the earliest earned positive points from the `positiveTransactions` list. But before that, we will first check if the same payer appears in the  `negativeTransaction` list (meaning payer withdraws points). If they do, full/part of the positive points are used to negate the nagetive points. Any remaining positive points will be used for spending. 


### Running Tests
Run tests in `test_app.py` from the project's main directory:
```
pytest
```
Tests check that the app should:
* `GET` all points by payer
* `POST` a new transaction
* `POST` spend points available
* NOT `POST` spend a negative/unavailable amount of points



