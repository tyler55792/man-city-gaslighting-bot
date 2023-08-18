import mysql.connector
import boto3
import json
from requests_oauthlib import OAuth1Session
from datetime import datetime

def get_tweet(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password, 
            database=database
        )
        
        if connection.is_connected():
            print("Connected to DB")
            
    except Exception as e:
        print("Error:", e)
    
    # Get current day, month, year
    now = datetime.now()
    day = now.strftime("%d")
    month = now.strftime("%m")
    year = now.strftime("%Y")
    
    # Query MySQL database
    cursor = connection.cursor()
    select_query = f'''
        SELECT * 
        FROM prem_results.results_table3 
        WHERE 
	        DAY(STR_TO_DATE(date_column, '%d/%m/%Y')) = {day}
	        AND MONTH(STR_TO_DATE(date_column, '%d/%m/%Y')) = {month}
	        AND ((HomeTeam='Man City' AND FTR='A') OR (AwayTeam='Man City' AND FTR='H'))
        ORDER BY ABS(FTHG-FTAG) DESC
        LIMIT 1;
        '''
    cursor.execute(select_query)
    results = cursor.fetchall()[0]
    cursor.close()
    connection.close()
    
    # Calculate number of years ago loss was
    loss_date = results[1] 
    try:
        # handle 4 digit year
        date_of_loss = datetime.strptime(loss_date, '%d/%m/%Y')
        years_ago_today = int(year) - int(date_of_loss.year)
    except:
        # handle 2 digit year
        date_of_loss = datetime.strptime(loss_date, '%d/%m/%y')
        years_ago_today = int(year) - int(date_of_loss.year)
    
    # Format tweet
    if results[3] != 'Man City':
        opponent_string = results[3]
    else:
        opponent_string = results[2]
    
    result_string = f"Exactly {years_ago_today} years ago today, Man City lost {results[5]}-{results[4]} to {opponent_string}."
    return result_string
    
def post_tweet(consumer_key, consumer_secret, resource_owner_key, resource_owner_secret, payload):
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret
    )
    
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )
    
    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    
    print("Response code: {}".format(response.status_code))
    return response.json()

def lambda_handler(event, context): 
    # Get db keys from parameter store
    client = boto3.client('ssm')
    db_parameters = client.get_parameters(
        Names=[
            'prem_host',
            'prem_user',
            'prem_password',
            'prem_database'
        ],
        WithDecryption=True
    )
    
    keys = {} 
    for parameter in db_parameters['Parameters']:
        keys[parameter['Name']] = parameter['Value']
    
    host=str(keys.get('prem_host'))
    user=str(keys.get('prem_user'))
    password=str(keys.get('prem_password'))
    database=str(keys.get('prem_database'))
    
    try:
        result_string = get_tweet(host, user, password, database)
    except:
        # man city has never lost on today's date, so don't tweet
        return
    
    # Get twitter keys from parameter store
    client = boto3.client('ssm')
    parameters = client.get_parameters(
        Names=[
            'twitter_consumer_key',
            'twitter_consumer_secret',
            'twitter_access_token',
            'twitter_access_token_secret'
        ],
        WithDecryption=True
    )
    
    keys = {} 
    for parameter in parameters['Parameters']:
        keys[parameter['Name']] = parameter['Value']
    
    consumer_key=keys.get('twitter_consumer_key') 
    consumer_secret=keys.get('twitter_consumer_secret')
    resource_owner_key=keys.get('twitter_access_token') 
    resource_owner_secret=keys.get('twitter_access_token_secret')
    
    payload = {"text": result_string}
    
    twitter_response = post_tweet(consumer_key, consumer_secret, resource_owner_key, resource_owner_secret, payload)

    return {
        'statusCode': 200,
        'body': json.dumps(twitter_response)
    }
    