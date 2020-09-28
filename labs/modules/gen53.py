#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
""" Route53 wrapper"""

# import python libs
import logging

# import libs
from modules import cfgen
from modules.utils.boto3client import _get_conn
import boto3

def record_set_present(domain, record, region):
    try:
        for hosted_zone in _get_conn(service='route53').list_hosted_zones()['HostedZones']:
            if hosted_zone['Name'] == domain + '.':
                hosted_zone_id = hosted_zone['Id'].split('/')[2]
                print(f'[53gen]\tfound HostedZoneId: {hosted_zone_id}')
    except Exception as err:
        logging.error(f'Zone: {domain} not found in hosted zones.')
        logging.error(f'error {err}')
    try:
        full_domain = f'{record}.{domain}'
        logging.debug(f'domain: {full_domain}')
        cloudfront_domain = cfgen.find_cloudfront_distribution(full_domain)
    except Exception as err:
        logging.error(f'error {err}')

    try:
        res = _get_conn(service='route53').change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Comment': f'RecordSet for {record}.{domain} with CloudFront',
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': f'{record}.{domain}',
                            'Type': 'CNAME',
                            'Region': region,
                            'SetIdentifier': 'SIMPLE',
                            'TTL': 60,
                            'ResourceRecords': [
                                {'Value': cloudfront_domain}
                                ]
                            }
                        }
                ]
            }
        )
        print(f'[53gen]\tcreated recordset for {record}.{domain} with {cloudfront_domain}')
    except Exception as err:
            logging.error(f'error {err}')
