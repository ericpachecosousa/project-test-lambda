import json
import urllib3
import boto3
import os
import base64

from base64 import b64decode

##Clientes do s3 e KMS
s3_client = boto3.client('s3')
kms_client = boto3.client('kms')

def lambda_handler(event, context):
    
    cep = event['queryStringParameters']['cep']
    
    if len(cep) != 8:
        return {
        'statusCode': 400,
        'body': json.dumps('Quantidade de dígitos inválida!', ensure_ascii=False).encode('utf8')
    }
    
    ##Request na API VIACEP
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://viacep.com.br/ws/{}/json/'.format(cep))

    
    ##Buscar nome do bucket criptografado
    s3NameEncrypted = os.environ['BUCKET_NAME']
    s3NameDecrypted = kms_client.decrypt(
    CiphertextBlob=b64decode(s3NameEncrypted),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')
    
    
    ##Buscar KeyId do KMS criptografado
    kmsKeyIdEncrypted = os.environ['MY_KEY']
    kmsKeyIdDecrypted = kms_client.decrypt(
    CiphertextBlob=b64decode(kmsKeyIdEncrypted),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')
    
    
    ##Criptografar conteudo
    conteudo = r.data
    conteudoCriptografado = kms_client.encrypt(KeyId=kmsKeyIdDecrypted, Plaintext=conteudo.decode('utf-8'))
    
    
    ##Salvar no S3
    ##Criptografar o bucket
    nomeArquivo = cep + '.txt'    
    s3_client.put_object(Bucket=s3NameDecrypted, Key=nomeArquivo, Body=conteudoCriptografado['CiphertextBlob'])
    
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Sucesso')
    }