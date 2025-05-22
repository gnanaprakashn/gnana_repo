import json
import boto3
import pymysql
import csv
import os
import io

RDS_HOST = os.environ['RDS_HOST']
RDS_USER = os.environ['RDS_USER']
RDS_PASS = os.environ['RDS_PASS']
RDS_DB = os.environ['RDS_DB']

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        
        body = json.loads(event['Records'][0]['body'])
        s3_info = body['Records'][0]['s3']

        bucket_name = s3_info['bucket']['name']
        object_key = s3_info['object']['key']

        print(f"Reading file from: s3://{bucket_name}/{object_key}")

        
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = s3_object['Body'].read().decode('utf-8', errors='replace')

        reader = csv.DictReader(io.StringIO(file_content), delimiter='\t')

        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASS,
            database=RDS_DB,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection:
            with connection.cursor() as cursor:
                for row in reader:
                    sql = """
                        INSERT INTO orders (
                            Category, City, Country, CustomerName, Manufacturer,
                            OrderDate, OrderID, PostalCode, ProductName, Region,
                            Segment, ShipDate, ShipMode, State, SubCategory,
                            Discount, Profit, Quantity, Sales
                        ) VALUES (
                            %(Category)s, %(City)s, %(Country)s, %(CustomerName)s, %(Manufacturer)s,
                            %(OrderDate)s, %(OrderID)s, %(PostalCode)s, %(ProductName)s, %(Region)s,
                            %(Segment)s, %(ShipDate)s, %(ShipMode)s, %(State)s, %(SubCategory)s,
                            %(Discount)s, %(Profit)s, %(Quantity)s, %(Sales)s
                        )
                    """
                    cursor.execute(sql, row)

            connection.commit()

        return {
            'statusCode': 200,
            'body': f"Successfully processed file: {object_key}"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Failed to process file: {object_key if 'object_key' in locals() else 'unknown'}"
        }
