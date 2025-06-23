#!/usr/bin/env python3
"""
Helper script to inspect the DynamoDB table schema
"""

import boto3
import os
import json
from pprint import pprint

# Set the table name to inspect
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'bloggs')

def describe_table():
    """
    Retrieve and print the DynamoDB table schema
    """
    try:
        # Create DynamoDB client
        dynamodb = boto3.client('dynamodb')
        
        # Call describe_table API
        response = dynamodb.describe_table(TableName=table_name)
        
        # Print table details
        print(f"\n=== Table Schema for {table_name} ===")
        
        # Key schema (primary key)
        print("\nKey Schema:")
        for key in response['Table'].get('KeySchema', []):
            key_type = 'Partition Key' if key['KeyType'] == 'HASH' else 'Sort Key'
            print(f"  {key['AttributeName']} ({key_type})")
        
        # Attribute definitions
        print("\nAttribute Definitions:")
        for attr in response['Table'].get('AttributeDefinitions', []):
            attr_type = {
                'S': 'String',
                'N': 'Number',
                'B': 'Binary'
            }.get(attr['AttributeType'], attr['AttributeType'])
            print(f"  {attr['AttributeName']}: {attr_type}")
        
        # GSIs
        if 'GlobalSecondaryIndexes' in response['Table']:
            print("\nGlobal Secondary Indexes:")
            for gsi in response['Table']['GlobalSecondaryIndexes']:
                print(f"  {gsi['IndexName']}:")
                for key in gsi.get('KeySchema', []):
                    key_type = 'Partition Key' if key['KeyType'] == 'HASH' else 'Sort Key'
                    print(f"    {key['AttributeName']} ({key_type})")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    describe_table()
