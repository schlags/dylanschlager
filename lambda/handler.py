# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
# import two packages to help us with dates and date formatting
import time

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('HelloWorldDatabase')

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    # store the current time in a human readable format in a variable
    for_js = int(int(time.time())) * 1000
    print(f"for_js: {for_js}")
# extract values from the event object we got from the Lambda service and store in a variable
    try:
        name = event['firstName'] +' '+ event['lastName']
        bringing = event['brings']
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
    response = table.put_item(
        Item={
            'ID': name,
            'Bringing': bringing,
            'Signed Up Time':str(for_js)
            })
# return a properly formatted JSON object
    if bringing != "":
        bringstring = f" You are now bringing {bringing}."
    else:
        bringstring = ""
    return {
        'statusCode': 201,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(f'Welcome, {name}.{bringstring} Please refresh the page.')
    }

print(lambda_handler("", ""))
print(lambda_handler({
    "firstName": "Dylan",
    "lastName": "Schlager",
    "brings": "Old Fashioned's"
    },""
    )
)