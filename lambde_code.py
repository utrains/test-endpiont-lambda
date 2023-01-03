import json
import boto3
import socket
import boto3

def lambda_handler(event, context):
    #calling the function with websites
    region="ca-central-1"
    senderemail="enter sender email"
    receiveremail="enter receiver email"
    S3bucket="enter s3 bucketname"
    websiteFile="websites.txt"
    sites=get_bucket_data(S3bucket,websiteFile)
    if is_verified_email(senderemail,receiveremail):
        for site in sites:
            if is_running(f'{site}'):
                #send_plain_email(senderemail,receiveremail,"Website is up", f"{site} is running!",region)
                print(f"{site} is running!")
            else:
                send_plain_email(senderemail,receiveremail,"Website is down",f'There is a problem with {site}! please verify',region)
                print(f'There is a problem with {site}!')
    else:
        print("verification email sent")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


#function to get all the verified email.
def get_list_of_verified_emails():
    # Create SES client
    ses = boto3.client('ses')

    response = ses.list_verified_email_addresses()
    print(response)
    return(response['VerifiedEmailAddresses'])
    
#function to send verification email.    
def verify_email(email):
    # Create SES client
    ses = boto3.client('ses')
    
    response = ses.verify_email_identity(
      EmailAddress = email
    )

    print(response)
    
#check if email is verified and send verification.
def is_verified_email(sender_email_address,receiver_email_address):
    verified_emails= get_list_of_verified_emails()
    setemail=[sender_email_address,receiver_email_address]
    print(setemail)
    # verifies if sender and receiver are verified then sends the message.
    if set(setemail).issubset(set(verified_emails)):
        return True
        #send_plain_email(sender_email_address,receiver_email_address,subject,message)
    else:
        # sends sends verification emails to the unverified email.
        unverified_emails=list(set(setemail)- set(setemail).intersection(set(verified_emails)))
        print(unverified_emails)
        for email in unverified_emails:
            verify_email(email)
        return False
        
        

#function to test if website is running
def is_running(site):
    """This function attempts to connect to the given server using a socket.
        Returns: Whether or not it was able to connect to the server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((site, 80))
        return True
    except:
        return False
#function to get the  data from S3 bucket
def get_bucket_data(bucketName,bucketObject):
    # getting the S3 object
    s3 = boto3.client('s3')
    data = s3.get_object(Bucket=bucketName, Key=bucketObject)
    contents = data['Body'].read().decode("utf-8")
    websites = contents.splitlines()
    return websites
def send_plain_email(sender,receiver,subject,message,region):
    ses_client = boto3.client("ses", region_name=region)
    CHARSET = "UTF-8"

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                receiver,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": message,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data":subject,
            },
        },
        Source=sender,
    )   
