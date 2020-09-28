#!/usr/bin/env python3
# -*- encoding: utf-8 -*--
""" S3 wrapper """
# import python libs
import logging
import magic
import os

# import libs
from modules.utils.boto3client import _get_conn


def create(bucket):
    try:
        list_buckets(bucket)
        set_policy(bucket)
        set_website(bucket)
    except Exception as err:
        logging.error(f'An error occured: {err}')


def list_buckets(bucket):
    try:
        res = _get_conn(service='s3').list_buckets()
        buckets = []
        for b in res['Buckets']:
            buckets.append(b['Name'].split('.')[0])
        if bucket not in buckets:
            create_bucket(bucket)
    except Exception as err:
        logging.error(err)


def create_bucket(bucket):
    """Creates the bucket, if not allready present"""
    try:
        # TODO: check if the bucket exists first
        res = _get_conn(service='s3').create_bucket(
                ACL='public-read',
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint':'EU'}
                )
        print(f'[s3gen]\tcreated/updated {bucket}')
    except Exception as err:
        logging.debug(err)


def set_policy(bucket):
    """Set's the bucket policy."""
    policy = '{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::' + bucket+ '/*"}]}'
    try:
        res =_get_conn(service='s3').put_bucket_policy(
            Bucket=bucket,
            ConfirmRemoveSelfBucketAccess=False,
            Policy=policy
            )
        print(f'[s3gen]\tset policy on {bucket}')
    except Exception as err:
        logging.error(err)


def set_website(bucket):
    """Turns the bucket into a static website."""
    conn = _get_conn(service='s3')
    try:
        res = conn.put_bucket_website(
                Bucket=bucket,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'},
                }
            )
        print(f'[s3gen]\tturned on Static Hosting for {bucket}')
    except Exception as err:
        logging.error(err)


def sync(bucket, output_dir):
    try:
        for item in os.listdir(output_dir):
            if item.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = magic.from_file(f'{output_dir}/{item}', mime=True)
            res = _get_conn(service='s3').put_object(
                Body=open(output_dir + '/' + item, 'rb'),
                Bucket=bucket,
                Key=item,
                ContentType=content_type,
            )
            print(f'[s3gen]\tsynced {item} to bucket: {bucket}')
    except Exception as err:
        logging.error(err)
