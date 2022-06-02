import json
import time
# import the AWS SDK (for Python the package name is boto3)
import boto3

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('BirthdaySchedule')

def deleteBar(id):
    table.delete_item(
        Key={
            'id': id
        }
    )
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(f'Bar deleted! {id}')
    }

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    print("Context: ", context)
# extract values from the event object we got from the Lambda service and store in a variable
    try:
        bar = event['id']
        arriveTime = event['arriveTime']
        leaveTime = event['leaveTime']
        address = event['address']
    except:
        try:
            bar = event['id']
            method = event['method']
            if method == "delete":
                return deleteBar(bar)
            else:
                # throw exception
                raise Exception("Invalid method")
        except:
            bars = table.scan()['Items']
            try:
                sorted_bars = sorted(bars, key = lambda i: (i['arriveTime']), reverse=False)
                print("Sorted.")
            except Exception as e:
                print("couldn't sort")
                sorted_bars = bars
                print(e)
            return {
                'statusCode': 200,
                'body': sorted_bars
            }
# write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    table.put_item(
        Item={
            'id': bar,
            'arriveTime':arriveTime,
            'leaveTime':leaveTime,
            'address':address
            })
# return a properly formatted JSON object
    return {
        'statusCode': 201,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(f'Bar added! {bar}, {arriveTime}, {leaveTime}, {address}')
    }
