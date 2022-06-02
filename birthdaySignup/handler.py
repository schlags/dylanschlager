import json
import time
# import the AWS SDK (for Python the package name is boto3)
import boto3

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('BirthdaySignup')

def deletePerson(id):
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
        'body': json.dumps(f'Person deleted! {id}')
    }


# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    print("Event: ", event)
    print("Context: ", context)
    # store the current time in a human readable format in a variable
    for_js = int(int(time.time())) * 1000
    print(f"for_js: {for_js}")
# extract values from the event object we got from the Lambda service and store in a variable
    try:
        if (event.has_key('method')) and (event.has_key('id')):
            if event['method'] == "delete":
                return deletePerson(event['id'])
            else:
                print('Invalid method presented.')
        name = event['firstName'] +' '+ event['lastName']
    except:
        people = table.scan()['Items']
        try:
            sorted_people = sorted(people, key = lambda i: (i['Signed Up Time']), reverse=True)
            print("Sorted.")
        except Exception as e:
            print("couldn't sort")
            sorted_people = people
            print(e)
        return {
            'statusCode': 200,
            'body': sorted_people
        }
# write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    table.put_item(
        Item={
            'id': name,
            'Signed Up Time':str(for_js)
            })
# return a properly formatted JSON object
    return {
        'statusCode': 201,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(f'Welcome, {name}. See you at the bar crawl!')
    }


print(lambda_handler({
    "firstName": "Dylan",
    "lastName": "Schlager",
    },""))
