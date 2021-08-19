#!/usr/bin/env python3
from flask import Flask, request, Response, abort, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session

import hide

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table    = dynamodb.Table('p4p3')

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
users = {
    1: User(1, hide.USERNAME, hide.PASSWORD)
}

# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def top():
    return redirect("/login/")

# ログインしないと表示されないパス
@app.route('/setting/',methods=['GET'])
@login_required
def setting():
   result = table.query(
       KeyConditionExpression=Key('user_id').eq('takeda'),
       Limit=1
   )
   d = result['Items'][0]
   item_name = d['item_name']
   item_weight = d['item_weight']
   item_count = d['item_count']
   values = {"name": item_name, "weight": item_weight, "count": item_count}
   return render_template('setting.html', \
       values=values, \
       login="true",)

@app.route('/home/')
@login_required
def home():
   result = table.query(
       KeyConditionExpression=Key('user_id').eq('takeda'),
       Limit=1
   )
   d = result['Items'][0]
   item_name = d['item_name']
   item_weight = d['item_weight']
   item_count = d['item_count']
   item_now = d['item_now']
   values = {"name": item_name, "weight": item_weight, "count": item_count, "now": item_now}
   return render_template('home.html', \
       values=values, \
       login="true",)

@app.route('/setting/', methods=['POST'])
@login_required
def form():
   name2 = request.form['name']
   weight2 = request.form['weight']
   count2 = request.form['count']
   response = table.update_item(
       Key={
           'user_id': str('takeda'),
           'timestamp': str(292479292)
       },
       UpdateExpression="set item_name=:n, item_weight=:w, item_count=:c",
        ExpressionAttributeValues={
            ':n': str(name2),
            ':w': str(weight2),
            ':c': str(count2)
        }
   )

   values = {"name": name2, "weight": weight2, "count": count2}

   return render_template('setting.html', \
       values=values, \
       login="true", \
       message = "設定が変更されました。",)



# ログインパス
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return redirect("/home/")
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)
