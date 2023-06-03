# Lambda to record a horse_id as a winner, find all bets on that horse, and pay out the winnings.
import json
import boto3

dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    print(f"Event {event}")
    method = event['requestContext']['http']['method']
    if method == 'POST':
        body = json.loads(event['body'])
        horse_id = body['horse_id']
        return record_and_pay(horse_id)
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }

from decimal import Decimal

def record_and_pay(horse_id):
    paid_response_body = {
        'winning_horse': horse_id,
        'players_paid': [],
        'bets': []
    }
    # Find all bets on this horse.
    try:
        response = dynamodb.Table('bets').scan(FilterExpression='horse_id = :horse_id', ExpressionAttributeValues={':horse_id': horse_id})
        bets = response['Items']
        print(f"Found bets: {bets}")
        paid_response_body['bets'] = bets
        # Find the odds for this horse.
        response = dynamodb.Table('raceOdds').get_item(Key={'horse_id': horse_id})
        odds = response['Item']['odds']
        race_name = response['Item']['race_name']
        print(f"Found odds: {odds}")
        print(f"Found race name: {race_name}")
        # Odds are in the format of things like 6/5 (which means for every 5 dollars you bet, you win 6 dollars).
        # We need to convert this to a decimal.
        odds = odds.split('/')
        odds = Decimal(odds[0]) / Decimal(odds[1])
        print(f"Converted odds: {odds}")
        # Pay out the winnings.
        for bet in bets:
            print(f"Found bet: {bet}")
            winnings = Decimal(bet['amount_wagered']) * odds
            print(f"Paying out {winnings}")
            dynamodb.Table('players').update_item(Key={'player_id': bet['player_id']}, UpdateExpression='ADD balance :winnings', ExpressionAttributeValues={':winnings': winnings})
            paid_response_body['players_paid'].append({'player_id': bet['player_id'], 'winnings': winnings})
            # Delete the bet.
            # dynamodb.Table('bets').delete_item(Key={'bet_id': bet['bet_id'], 'player_id': bet['player_id']})
            # print(f"Deleted bet: {bet}")
        
        # Delete all records in the bets table
        # Specify the table name
        table_name = 'bets'

        # Scan the table to retrieve all items
        response = dynamodb.Table('bets').scan()

        # Delete each item in the table
        for bet in response['Items']:
            dynamodb.Table('bets').delete_item(Key={'bet_id': bet['bet_id'], 'player_id': bet['player_id']})

        # Print the result
        print(f"All items in '{table_name}' table have been deleted.")

        # Delete all raceOdds entries for the race_name
        response = dynamodb.Table('raceOdds').scan(FilterExpression='race_name = :race_name', ExpressionAttributeValues={':race_name': race_name})
        raceOdds_to_delete = response['Items']

        for raceOdds in raceOdds_to_delete:
            dynamodb.Table('raceOdds').delete_item(Key={'horse_id': raceOdds['horse_id']})
            print(f"Deleted raceOdds: {raceOdds}")

        return {
            'statusCode': 200,
            'body': json.dumps(paid_response_body, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
