import json
import boto3
import uuid

# races should look like
#   {
#     "horse_id": "horse_id",
#     "race_name": "race_name",
#     "odds": "odds"
#   }


dynamodb = boto3.resource('dynamodb')
table_name = 'raceOdds'

def lambda_handler(event, context):
    print(f"Event {event}")
    method = event['requestContext']['http']['method']
    if method == 'GET':
        return get_all_race_odds()
    elif method == 'POST':
        body = json.loads(event['body'])
        new_odds = {
            'horse_id': body['horse_id'],
            'race_name': body['race_name'],
            'odds': body['odds']
        }
        return create_race_odd(new_odds)
        
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

def get_all_race_odds():
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        odds = response['Items']
        return {
            'statusCode': 200,
            'body': json.dumps(odds),
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

def create_race_odd(new_odd):
    try:
        table = dynamodb.Table(table_name)
        # First check that the player doesn't already exist.
        response = table.get_item(Key={'horse_id': new_odd['horse_id']})
        if 'Item' in response:
            print(f"FOUND ITEM: {response['Item']}")
            return {
                'statusCode': 400,
                'body': 'Horse in that race already exists',
                'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                },
            }
        response = table.put_item(Item=new_odd)
        return {
            'statusCode': 201,
            'body': 'Horse odds added successfully',
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
