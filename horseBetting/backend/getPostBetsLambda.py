import json
import boto3
import uuid
from decimal import Decimal

# bets should look like
# {
#     "bet_id": "random_uuid",
#     "player_id": "player_id",
#     "amount_wagered": 100,
#     "horse_id": "jeff",
#     "odds": "6/3"
# }

dynamodb = boto3.resource('dynamodb')
table_name = 'bets'
player_table_name = 'players'
races_table_name = 'raceOdds'

def lambda_handler(event, context):
    print(f"Event {event}")
    method = event['requestContext']['http']['method']
    if method == 'GET':
        return get_all_bets()
    elif method == 'POST':
        body = json.loads(event['body'])
        new_bet = {
            'player_id': body['player_id'],
            'horse_id': body['horse_id'],
            'amount_wagered': body['amount_wagered']
        }
        return create_bet(new_bet)
        
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed',
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            },
        }



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def get_all_bets():
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        bets = response['Items']
        return {
            'statusCode': 200,
            'body': json.dumps(bets, cls=DecimalEncoder),
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

def create_bet(new_bet):
    try:
        bets_table = dynamodb.Table(table_name)
        players_table = dynamodb.Table(player_table_name)
        races_table = dynamodb.Table(races_table_name)
        # First find the race and horse to get the odds.
        horse_id = new_bet['horse_id']
        response = races_table.get_item(Key={'horse_id':  horse_id})
        if 'Item' not in response:
            return {
                'statusCode': 400,
                'body': 'That horse does not exist',
                'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                },
            }
        odds = response['Item']['odds']
        # Now find the player to get the balance.
        player_id = new_bet['player_id']
        response = players_table.get_item(Key={'player_id': player_id})
        if 'Item' not in response:
            return {
                'statusCode': 400,
                'body': '{\'message\': \'That player does not exist\'}',
                'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                },
            }
        balance = response['Item']['balance']
        # Now check that the player has enough money to make the bet.
        amount_wagered = new_bet['amount_wagered']
        if amount_wagered > balance:
            return {
                'statusCode': 400,
                'body': '{\'message\': \'Player does not have enough money to make that bet\'}',
                'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                },
            }
        # Now create the bet.
        new_bet['odds'] = odds

        # Generate a random UUID for the bet_id
        new_bet['bet_id'] = str(uuid.uuid4())

        response = bets_table.put_item(Item=new_bet)
        # Now update the player's balance.
        new_balance = balance - amount_wagered
        response = players_table.update_item(
            Key={'player_id': player_id},
            UpdateExpression='SET balance = :val1',
            ExpressionAttributeValues={
                ':val1': new_balance
            }
        )
        return {
            'statusCode': 201,
            'body': '{\'message\': \''+f"Bet created for {new_bet['player_id']} with {new_bet['amount_wagered']} amount and {new_bet['odds']} odds"+'\'}',
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
