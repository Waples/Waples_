#!/usr/bin/env python3
# -*- encoding: utf-8 -*--
"""
ACM Wrapper
"""

# import python libs
import logging
import time

# import aws libs
import boto3

# import modules
from modules.utils import idgen
from modules.utils.boto3client import _get_conn


def certificate_present(fqdn, domain):
    domain = f'*.{domain}'
    print(f'[acm  ]\t domain: {domain}')
    if not get_certs(domain):
        request_cert(domain)
        print('\tthere is a slight delay, so we wait 5 seconds for the API.')
        time.sleep(5)
    validate_certificate(fqdn, domain)
    return get_certs(domain)


def get_certs(domain):
    ret = False
    req = _get_conn(service='acm', region='us-east-1').list_certificates()
    for item in req['CertificateSummaryList']:
        if item['DomainName'] == domain:
            if item['CertificateArn']:
                ret = item['CertificateArn']
            else:
                print('[acm  ]\tfucking fix this')
    return ret


def validate_certificate(fqdn, domain):
    arn = get_certs(domain)
    print(f'[acm  ]\tARN to validate: {arn}')
    data = _get_conn(service='acm', region='us-east-1').describe_certificate(CertificateArn=arn)
    dns_name = data['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Name']
    dns_value = data['Certificate']['DomainValidationOptions'][0]['ResourceRecord']['Value']
    for hosted_zone in boto3.client('route53').list_hosted_zones()['HostedZones']:
        if hosted_zone['Name'] == 'freyrsvin.nl.':
            hosted_zone_id = hosted_zone['Id'].split('/')[2]
    ret = boto3.client('route53').change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': f'RecordSet for ACM Validation',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'CNAME',
                        'TTL': 60,
                        'ResourceRecords': [
                            {'Value': dns_value}
                            ]
                        }
                    }
            ]
        }
    )
    while _get_conn(service='acm', region='us-east-1').describe_certificate(CertificateArn=arn)['Certificate']['Status'] == 'PENDING_VALIDATION':
        print(f'The certificate for {domain} is pending validation, waiting...')
        time.sleep(10)
    return(ret)


def request_cert(domain):
    res = _get_conn(service='acm', region='us-east-1').request_certificate(
        DomainName=domain,
        ValidationMethod='DNS',
        IdempotencyToken=idgen.id_gen(size=32)
    )
    ret = res['CertificateArn']
    print(f'[acm  ]\trequest_cert result: {ret}')
    return ret
