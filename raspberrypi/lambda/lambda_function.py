import json
from base64 import b64decode
import requests
import os
import urllib.parse
import urllib.request
import datetime
import decimal
import boto3
from boto3.dynamodb.conditions import Key


# LINE環境変数設定
line_notify_api = os.environ.get('line_notify_api')
line_notify_token = os.environ.get('line_notify_token')
IPADDR = os.environ.get('ipaddress')

def lambda_handler(event, context):
    # DynamoDBオブジェクトを取得
    dynamoDB = boto3.resource('dynamodb')
    table= dynamoDB.Table('p4p')
    #データをDynamoDBへ保存
    table.put_item(
        Item = {
            'device_id': event["device_id"],
            'weight': event["weight"],
            'timestamp': event["timestamp"],
            'flag': 3
        }
    )
    
    
    #設定情報を取得
    table2= dynamoDB.Table('p4p3')
    result = table2.query(
        KeyConditionExpression=Key('user_id').eq('takeda'),
        Limit=1
    )
    d = result['Items'][0]
    item_name = d['item_name']
    item_weight = d['item_weight']
    item_count = d['item_count']

    #現在の個数を計算、DBへ保存
    f = int(event["weight"]) / int(item_weight)
    
    if round(f) < 0:
        f = 0
    
    response = table2.update_item(
       Key={
           'user_id': str('takeda'),
           'timestamp': str(292479292)
       },
       UpdateExpression="set item_now=:a",
        ExpressionAttributeValues={
            ':a': str(round(f))
        }
    )

    #LINE通知設定
    if int(round(f)) <= int(item_count):
        message = ("\n" + item_name + "が残り" + str(round(f)) + "個になりました。\n購入をお願いします。\n\nポータル：" + IPADDR)
        return notify_to_line(message)


def notify_to_line(message):
    method = "POST"
    headers = {"Authorization": "Bearer " + line_notify_token}
    payload = {"message": message}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(line_notify_api, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
        return message
    except Exception as e:
        return e
