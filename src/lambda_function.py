import json
from main import main


def lambda_handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(e)
        }
