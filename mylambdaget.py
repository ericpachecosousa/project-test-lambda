import json
import boto3
import urllib
import os
import base64

from base64 import b64decode

sesClient = boto3.client('ses')
s3_client = boto3.client('s3')
kms_client = boto3.client('kms')

def lambda_handler(event, context):
    ##Buscar object_key e nome do Bucket através do evento
    ##bucket = event['Records'][0]['s3']['bucket']['name']
    ##key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    ##teste
    for record in event['Records']:
        jsonmaybe=(record["body"])
        jsonmaybe=json.loads(jsonmaybe)
        bucket = jsonmaybe["Records"][0]["s3"]["bucket"]["name"]
        key=jsonmaybe["Records"][0]["s3"]["object"]["key"]
        
        objetoCriptografado = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
        
        objetoDecriptografado = kms_client.decrypt(CiphertextBlob=objetoCriptografado)['Plaintext'].decode('utf-8')
            
        body = objetoDecriptografado
        client = boto3.client('sns')
        response = client.publish(
            TargetArn=os.environ['SNS_ARN'],
            Message=json.dumps({'default': json.dumps(body),
                                'sms': '',
                                'email': body}),
            Subject='Envio Teste',
            MessageStructure='json'
        )
    return {
        'statusCode': 200,
        'body': json.dumps('Email enviado com sucesso!')
    }
            