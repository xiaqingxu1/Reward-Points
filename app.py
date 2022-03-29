from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

balance = 0  # total points
accounts = {}  # dictionary containing 'payer'-'points' pairs
earnings = []   # list of all transanctions with positive points 
withdraws = []   # list of transactins with negative points(used to withdraws positve points from same payer)

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
    3.earnings and withdraws 
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

    # updating withdraws and earnings, sorting earnings by timestamp
    if points < 0: 
        withdraws.append([payer, points, datetime_obj])
    else: 
        low, high = 0, len(earnings)
        while low < high:
            mid = low + high >> 1
            if datetime_obj > earnings[mid][2]:
                high = mid
            else:
                low = mid + 1
        earnings.insert(low, [payer, points, datetime_obj]) 

    return ("Points added successfully!", 200, content_header)  
           

@app.route('/spend_points', methods=['POST'])
def spend_points():
    """ Spending causes deducting points from earliest transaction in earnings. But before deduction, 
        one first check if the same payer withdraws points (if payer exists in withdraws). 
    ** If yes, payer's points is used to balance out the negative points first. 
       One premise used here: earliest earned points from same payer will be withdrawsn first.  
    ** After withdraws/if no withdraws, remaining points will then be applied towards spending.
    
    Spending points will cause FOUR updates: 
    1. balance 
    2. accounts 
    3. earnings and withdraws  
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
        
        # 2.updating earnings and withdraws
        while points > 0:
            posiT = earnings.pop()
            payer = posiT[0] 

            # search withdraws to see if earned points should be negated                 
            if withdraws and payer in [t[0] for t in withdraws]:
                for negaT in withdraws:
                    if negaT[0] == payer and posiT[1] + negaT[1] < 0:   # fully negated and not enough
                        negaT[1] += posiT[1]                           
                        break
                    elif negaT[0] == payer and posiT[1] + negaT[1] == 0: # fully negated, just enough
                        withdraws.remove(negaT)
                        break
                    elif negaT[0] == payer and posiT[1] + negaT[1] > 0:  # partially negated, points remaining
                        withdraws.remove(negaT)
                        posiT[1] += negaT[1] 
            
            if posiT[1]: 
                if posiT[1] > points: 
                    posiT[1] -= points 
                    earnings.append(posiT)   
                    paid, points = points, 0 
                else:                
                    paid = posiT[1]    
                    points -= posiT[1]       

                # updating accounts and spendignHistory           
                accounts[payer] -= paid                
                spendingHistory.append({"payer": payer, "points": -paid})                  
    return  jsonify(spendingHistory)


if __name__ == '__main__':
    app.run(debug=True)

