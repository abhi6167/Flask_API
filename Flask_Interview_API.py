# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 23:21:51 2021

@author: User
"""

from flask import Flask
from flask_restful import Api,Resource,reqparse,abort
from datetime import datetime, date
import pandas as pd

app = Flask(__name__)

#to wrap our app into API
api = Api(app)



today = date.today()
def check_date(date_input):
    try:
        valid_date = datetime.strptime(date_input, '%d/%m/%Y').date()
        if not (today < valid_date ):
            return False
        return True
    except ValueError:
        return False


carddetails = reqparse.RequestParser()
carddetails.add_argument("cardnumber",    type=str,help="please provide the card number",required = True)
carddetails.add_argument("cardholdername",type=str,help="Please enter the name of the card holder",required=True)
carddetails.add_argument("expdate",       type=lambda x: x if check_date(x) else abort(404),help="Please enter the valid date and date should be in the format %d/%m/%Y and also date must be the future date",required=True)
carddetails.add_argument("Scode",         type=lambda x: x if (len(x)==3) or (len(x) == 0) else abort(404),help="Security code should be of 3 digits only")
carddetails.add_argument("Amount",        type=float,help="Please enter the amount",required=True)




bank_db = pd.read_csv("E:\\django_interview\\input_data.txt")
        
class External_payment_processing():
    
    def __init__(self,withdwal_money):
        self.withdwal_money = withdwal_money
    
    def CheapPaymentGateway(self,bankbalance):
        if float(bankbalance) - float(self.withdwal_money) < 0:
            return "Invalid"
        else:
            return float(bankbalance) - float(self.withdwal_money)
    
    def ExpensivePaymentGateway(self,bankbalance):
        if float(bankbalance) - float(self.withdwal_money) < 0:
            Status = External_payment_processing.CheapPaymentGateway(self,bankbalance)
            if Status == "Invalid":
                return "Invalid"
            else:
                return Status
        else:
            return float(bankbalance) - float(self.withdwal_money)

    def PremiumPaymentGateway(self,bankbalance):
        if float(bankbalance) - float(self.withdwal_money) < 0:
            for i in range(0,3):
                Status = External_payment_processing.CheapPaymentGateway(self,bankbalance)
                if Status == "Invalid":
                    pass
                else:
                    return Status
            return "Invalid"
        else:
            return float(bankbalance) - float(self.withdwal_money)
    
class paymentprocess(Resource):
    
    def put(self):   
        args = carddetails.parse_args()
        
        withdwal_money = args["Amount"]
        cardnumber = str(args["cardnumber"])
        
        bank_db["cardnumber"] = bank_db["cardnumber"].astype(str)
        customer_details = bank_db[bank_db["cardnumber"] == cardnumber]
        
        
        if (customer_details.shape[0] == 0) :
            abort(404,message="Card Number is invalid")
        else:
            amount = External_payment_processing(withdwal_money)
            Balance = customer_details["Amount"].tolist()[0]
            if withdwal_money < 20:
                Transcation_status = amount.CheapPaymentGateway(Balance)
                
            elif (withdwal_money > 21) and (withdwal_money < 500):
                Transcation_status = amount.ExpensivePaymentGateway(Balance)
                
            else:
                Transcation_status = amount.PremiumPaymentGateway(Balance)
                
        if Transcation_status == "Invalid":
            return {"Transcation Failed":"Since the balance is less than the requested money",
                    "Reuest is invalid":"400 Bad Request"},400
        else:
            return {"Available Balacne":Transcation_status,
                    "Status":"Payment is processed: 200 OK"},200

#Specifyin gthe accessable url
api.add_resource(paymentprocess,"/Etranscation")



if __name__ == "__main__":
    app.run(debug = True)