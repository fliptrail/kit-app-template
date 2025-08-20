#!/usr/bin/env python3
import boto3
import csv
from botocore import UNSIGNED
from botocore.config import Config
from pathlib import Path

def generate_usd_csv_combined(buckets, output_file='usd_assets_cache.csv'):
    """Generate CSV file with USD asset metadata from multiple S3 buckets"""
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    paginator = s3.get_paginator('list_objects_v2')

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['_url', 'filename', 'directory', 'bucket', 'size', 'last_modified', 'keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for bucket_config in buckets:
            bucket_name = bucket_config['bucket_name']
            prefix = bucket_config['prefix']
            print(f"Processing bucket: {bucket_name}, prefix: {prefix}")

            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    path_obj = Path(key)

                    if (path_obj.name.endswith('.usd')):

                        # Extract keywords from path
                        keywords = extract_keywords(key)

                        writer.writerow({
                            '_url': f"https://omniverse-content-production.s3-us-west-2.amazonaws.com/{key}",
                            'filename': path_obj.name,
                            'directory': str(path_obj.parent),
                            'bucket': bucket_name,
                            'size': obj.get('Size', 0),
                            'last_modified': obj.get('LastModified', '').isoformat() if obj.get('LastModified') else '',
                            'keywords': ' '.join(keywords)
                        })

    print(f"Generated {output_file} with USD asset data from {len(buckets)} bucket configurations")

def extract_keywords(path):
    """Extract searchable keywords from file path"""
    keywords = set()

    # Split path into components
    path_parts = Path(path).parts
    for part in path_parts:
        # Add the part itself
        keywords.add(part.lower())

        # Split on common separators
        for separator in ['_', '-', '.', ' ']:
            if separator in part:
                keywords.update(part.lower().split(separator))

    # Remove empty strings and common words
    stop_words = {'', 'usd', 'usda', 'usdc', 'assets', 'models', 'materials'}
    keywords = {k for k in keywords if k and k not in stop_words and len(k) > 1}

    return list(keywords)

if __name__ == "__main__":

    buckets = [
        {
            'bucket_name': 'omniverse-content-production',
            'prefix': 'Assets/DigitalTwin/Assets/'
        },
        {
            'bucket_name': 'omniverse-content-production',
            'prefix': 'Assets/ArchVis/'
        },
        {
            'bucket_name': 'omniverse-content-production',
            'prefix': 'Assets/Vegetation/'
        },
        {
            'bucket_name': 'omniverse-content-production',
            'prefix': 'Assets/Isaac/4.5/Isaac/'
        },
    ]

    # Generate combined CSV with all buckets
    generate_usd_csv_combined(buckets)
