import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def transformar_datos(json_data):
    transformed_data = {}
    for key, value in json_data.items():
        if 'S' in value:
            transformed_data[key] = value['S']
        elif 'N' in value:
            transformed_data[key] = int(value['N'])
    return transformed_data

def lambda_handler(event, context):
    # Recorrer registros del evento SQS
    for record in event['Records']:
        try:
            # Obtener el cuerpo del mensaje SQS
            sqs_body = json.loads(record['body'])
            
            # Extraer los datos relevantes del evento DynamoDB
            dynamodb_data = sqs_body['dynamodb']
            new_image = dynamodb_data['NewImage']
            
            # Transformar los datos
            transformed_data = transformar_datos(new_image)
            
            # Construir el nombre del archivo en S3
            file_name = f"libro_{transformed_data['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            
            # Guardar los datos transformados en un archivo en S3
            s3.put_object(
                Bucket='bucket-aws-libros-franciscod3v-2024',
                Key=file_name,
                Body=json.dumps(transformed_data),
                ContentType='application/json'
            )
            
            logger.info(f"Archivo guardado en S3: {file_name}") #Se podrá ver desde Cloudwatch
        except Exception as e:
            logger.error(f"Error al procesar el mensaje: {e}")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Datos transformados y almacenados en S3 exitosamente')
    }