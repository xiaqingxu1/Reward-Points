from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

balance = 0  # total points
accounts = {}  # dictionary containing 'payer'-'points' pairs
positiveTransactions = []   # list of all transanctions with positive points 
negativeTransactions = []   # list of transactins with negative points(used to withdraw positve points from same payer)

content_header = {}  
content_header["Content-type"] = "application/json" 

@app.route('/')
def home():
    return "Home Page"

@app.route('/check_balance')
def check_balance(): 
    return jsonify(accounts)
   

@app.route('/add_transactions', methods=['POST'])
def add_transactions():   
    """ Since transactions with positive/negative points are not necessrily added on the order of the transaction timestamp.
    So DID NOT place any restrictions on adding transactions. The premise used here is that after adding transactions, points from 
    same payer will not go below zero.  
    Adding one transaction will cause THREE updates: 
    1.balance 
    2.accounts 
    3.positiveTransactions and negativeTransaction 
    """    
    global balance 
    data = request.get_json(force=True)  
    payer = data['payer']
    points = int(data['points'])
    datetime_obj = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    
    # updating balance
    balance += points

    # updating accounts
    if payer in accounts: 
        accounts[payer] += points
    else:
        accounts[payer] = points

    # updating negativeTransanctions and positiveTransactions, sorting positiveTransanctions by datetime
    if points < 0: 
        negativeTransactions.append([payer, points, datetime_obj])
    else: 
        low, high = 0, len(positiveTransactions)
        while low < high:
            mid = low + high >> 1
            if datetime_obj > positiveTransactions[mid][2]:
                high = mid
            else:
                low = mid + 1
        positiveTransactions.insert(low, [payer, points, datetime_obj]) 

    return ("Points added successfully!", 200, content_header)  
           

@app.route('/spend_points', methods=['POST'])
def spend_points():
    """ Spending causes deducting points from postiveTransactions. But before deduction, 
        one first check if the same payer withdraws points (if payer exists in negativeTransactions). 
    ** If yes, payer's points is used to balance out the negative points first. 
       One premise used here: earliest earned points will be withdrawn first.  
    ** After withdraw/if no withdraw, remaining points will then be applied towards spending.
    
    Spending points will cause FOUR updates: 
    1. balance 
    2. accounts 
    3. positiveTransactions and negativeTransactions  
    4. spendingHistory
    """
       
    global balance
    data = request.get_json(force=True)
    points = int(data['points'])
    spendingHistory = [] 
    
    ### negative spending will error
    if points <= 0:
        return ("CAN NOT SPEND NEGATIVE POINTS!!!", 400)

    ### over spending will error    
    elif points > balance:   
        return ("INSUFFICIENT POINTS!!!", 400) 

    ### allowed spending
    else:  
        # 1.updating balance
        balance -= points                          
        
        # 2.updating positiveTransactions and negativeTransactions
        while points > 0:
            posiT = positiveTransactions.pop()
            payer = posiT[0] 

            # search negativeTransactions to see if earned points was withdrawn                 
            if negativeTransactions and payer in [t[0] for t in negativeTransactions]:
                for negaT in negativeTransactions:
                    if negaT[0] == payer and posiT[1] + negaT[1] < 0:   # fully withdrawn and not enough
                        negaT[1] += posiT[1]                           
                        break
                    elif negaT[0] == payer and posiT[1] + negaT[1] == 0: # fully withdrawn, just enough
                        negativeTransactions.remove(negaT)
                        break
                    elif negaT[0] == payer and posiT[1] + negaT[1] > 0:  # partially withdawn, points remaining to spend
                        negativeTransactions.remove(negaT)
                        posiT[1] += negaT[1] 
            
            if posiT[1]: 
                if posiT[1] > points: 
                    posiT[1] -= points 
                    positiveTransactions.append(posiT)   
                    paid, points = points, 0 
                else:                
                    paid = posiT[1]    
                    points -= posiT[1]       

                # updating accounts and spendignHistory           
                accounts[payer] -= paid                
                spendingHistory.append({"payer": payer, "points": -paid})                  
    print(negativeTransactions, positiveTransactions)
    return  jsonify(spendingHistory)


if __name__ == '__main__':
    app.run(debug=True)

