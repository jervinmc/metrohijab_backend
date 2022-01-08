#Imports
import string
import random
import smtplib
import sklearn
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Response
from flask import Flask, jsonify, request,redirect
from flask_restful import Resource, Api
from flask_cors import CORS
from decouple import config
from datetime import datetime
import requests
now = datetime.now().date()
from functools import wraps
import time
from Database import Database
app=Flask(__name__)
CORS(app)
api=Api(app)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Products(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        try:
            self.db.insert(f"INSERT INTO products values(default,{data.get('quantity')},{data.get('price')},'{data.get('user_id')}','{data.get('productName')}')")
            return {"status":"success"}
        except Exception as e:
            print(e)

    def get(self,category=None,pk=None):
        try:
            res = self.db.query(f"select * from sales where user_id='{pk}' order by id desc ")
            if(res==[]):
                return None
            else:
                listitem=[{"quantity":i[3],"price":i[4],"id":i[0],"product_name":i[2]} for i in res]
                return listitem
        except Exception as e:
            print(e)
            return {"status":f"{e}"}
    
    def delete(self,pk=None):
        data = request.get_json()
        try:
            self.db.insert(f"DELETE FROM products where id={data.get('product_id')} ")
            return {"status":"success"}
        except Exception as e:
            print(e)

class Reports(Resource):
    def __init__(self):
        self.db=Database()
    def get(self,pk=None):
        total_products = self.db.query(f"SELECT SUM(price*quantity) FROM products where user_id='{pk}'")
        total_sales = self.db.query(f"SELECT SUM(price*quantity) FROM sales where user_id='{pk}'")
        return {"total_products":f"{total_products[0][0]}","total_sales":f"{total_sales[0][0]}"}

class Sales(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        try:
            self.db.insert(f"INSERT INTO sales values(default,'{data.get('user_id')}','{data.get('product_name')}',{data.get('quantity')},{data.get('total_price')},{data.get('price')})")
            self.db.insert(f"UPDATE products set quantity=quantity-{data.get('quantity')} where id={data.get('product_id')}")
            return {"status":"success"}
        except Exception as e:
            print(e)

    def get(self,category=None,pk=None):
        try:
            res = self.db.query(f"select * from products where user_id='{pk}' order by id desc ")
            if(res==[]):
                return None
            else:
                listitem=[{"quantity":i[1],"price":i[2],"id":i[0],"product_name":i[4]} for i in res]
                return listitem
        except Exception as e:
            print(e)
            return {"status":f"{e}"}



class ResetPassword(Resource):
    def __init__(self):
        self.db=Database()
        
    def post(self):
        res = request.get_json()
        pw = id_generator()
        print(res)
        self.db.insert(f"UPDATE users set password='{pw}' where email='{res.get('email')}' ")
        msg = MIMEMultipart()
        msg.add_header('Content-Type', 'text/html')
        msg['To'] = str(res.get('email'))
        msg['Subject'] = "Reset password from Chatmind"
        part1=MIMEText("""\
            <html>
                <body>
                    Here's your new password : """+pw+"""
                </body>
            </html>
            
            """,'html')

        msg.attach(part1)
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login('jmacalawapersonal@gmail.com', "wew123WEW")
        # send the message via the server.
        server.sendmail('jmacalawapersonal@gmail.com', msg['To'], msg.as_string())

        server.quit()
        
        print("successfully sent email to %s:" % (msg['To']))
        
        return {"status":"success"}

class Usermanagement(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        data_fetch = self.db.query(f"select * from users where email='{data.get('email')}'")
        if(len(data_fetch)>0):
            return {"status":"Failed Input"}
        try:
            self.db.insert(f"INSERT INTO users(email,password) values('{data.get('email')}','{data.get('password')}')")
            return {"status":"success"}
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}

    def get(self,pk=None):
        if pk==None:
            res = self.db.query('SELECT * FROM users')
        else:
            res = self.db.query(f'SELECT * FROM users where id={pk}')
        return {"data":res}

    def delete(self,pk):
        try:
            self.db.insert(f'DELETE FROM users where id={pk}')
            return {"data":"success"}
        except:
            return {"status":"Failed"}
    
    def put(self,pk=None):
        data = request.get_json()
        print(data)
        try:
            isValid = self.db.query(f"select * from users where email='{data.get('email')}' and id={data.get('id')}")
            if(len(isValid)==0):
                data_fetch = self.db.query(f"select * from users where email='{data.get('email')}'")
                if(len(data_fetch)>0):
                    return {"status":"Failed Input"}
            if(data.get('password')=='' or data.get('password')==None):
                self.db.insert(f"UPDATE users set email='{data.get('email')}' where id={pk}")
            else:
                self.db.insert(f"UPDATE users set email='{data.get('email')}',password='{data.get('password')}' where id={pk}")
            print("saved")
            return {"status":"Success"}
        except Exception as e:
            print(e)
            return {"status":"Failed"}


class Register(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        data_fetch = self.db.query(f"select * from users where email='{data.get('email')}'")
        
        if(len(data_fetch)>0):
            return {"status":"Failed Input"}
        try:
            id = self.db.query("select max(id)+1 from users")
            res = self.db.insert(f"INSERT INTO users values({id[0][0]},'{data.get('email')}','{data.get('password')}')")
            return Response({"status":"Success"},status=201)
            
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}

class Login(Resource):
    def __init__(self):
        self.db=Database()

    def post(self,pk=None):
        data = request.get_json()
        print(data)
        try:
            res = self.db.query(f"SELECT * FROM users where email='{data.get('email')}' and password='{data.get('password')}'")
            if(res==[]):
                print(res)
                return {"status":"Wrong Credentials"}
            else:
                return {"status":"success","id":res[0][0],"email":res[0][1]}
            
        except Exception as e:
            print(e)
            return {"status":"Failed Input"}

api.add_resource(Usermanagement,'/api/v1/users/<int:pk>')
api.add_resource(Login,'/api/v1/login')
api.add_resource(Products,'/api/v1/products/<int:pk>')
api.add_resource(Sales,'/api/v1/sales/<int:pk>')
api.add_resource(Register,'/api/v1/register')
api.add_resource(ResetPassword,'/api/v1/reset')
api.add_resource(Reports,'/api/v1/reports/<int:pk>')
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=config("PORT"))