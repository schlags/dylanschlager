import json
import boto3
import uuid

# Refactor to accept the following body:
# {'version': '2.0', 'routeKey': 'POST /players', 'rawPath': '/players', 'rawQueryString': '', 'headers': {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'content-length': '61', 'content-type': 'application/json', 'host': '6g125mlu01.execute-api.us-east-1.amazonaws.com', 'postman-token': 'bfd2599e-5e5b-4782-9e8a-229edeb31e71', 'user-agent': 'PostmanRuntime/7.29.0', 'x-amzn-trace-id': 'Root=1-647a7f96-121491cf0391fc10393d4a22', 'x-forwarded-for': '71.33.145.191', 'x-forwarded-port': '443', 'x-forwarded-proto': 'https'}, 'requestContext': {'accountId': '806320764941', 'apiId': '6g125mlu01', 'domainName': '6g125mlu01.execute-api.us-east-1.amazonaws.com', 'domainPrefix': '6g125mlu01', 'http': {'method': 'POST', 'path': '/players', 'protocol': 'HTTP/1.1', 'sourceIp': '71.33.145.191', 'userAgent': 'PostmanRuntime/7.29.0'}, 'requestId': 'F6jfgg2WoAMEJVA=', 'routeKey': 'POST /players', 'stage': '$default', 'time': '02/Jun/2023:23:47:34 +0000', 'timeEpoch': 1685749654179}, 'body': '{\n  "player_id": "1234",\n  "name": "Dylan",\n  "score": "50"\n}', 'isBase64Encoded': False}


dynamodb = boto3.resource('dynamodb')
table_name = 'players'

def lambda_handler(event, context):
    print(f"Event {event}")
    method = event['requestContext']['http']['method']
    if method == 'GET':
        return get_all_players()
    elif method == 'POST':
        body = json.loads(event['body'])
        new_player = {
            'player_id': body['name'],
            'balance': 500
        }
        return create_player(new_player)
        
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed',
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }

from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def get_all_players():
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        players = response['Items']
        players = sorted(players, key=lambda x: x['balance'], reverse=True)
        
        return {
            'statusCode': 200,
            'body': json.dumps(players, cls=DecimalEncoder),
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e),
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }

def create_player(new_player):
    try:
        table = dynamodb.Table(table_name)
        # First check that the player doesn't already exist.
        response = table.get_item(Key={'player_id': new_player['player_id']})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': 'Player already exists',
                'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                },
            }
        response = table.put_item(Item=new_player)
        return {
            'statusCode': 201,
            'body': 'Player created successfully',
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e),
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }
