#!/usr/bin/env python3
# -*- encoding: utf-8 -*--
"""
CloudFront Wrapper
"""

# import python libs
import boto3
import logging
import yaml
import random
import string
from modules import acmgen
from modules.utils.boto3client import _get_conn
from modules.utils import idgen

def find_cloudfront_distribution(domain):
    ret = f'Something is very wrong here.....'
    data = boto3.client('cloudfront').list_distributions()
    for item in data['DistributionList']['Items']:
        if item['Origins']['Items'][0]['Id'] == domain:
            res = item['Id']
            dist = _get_conn(service='cloudfront').get_distribution(Id=res)
            ret = dist['Distribution']['DomainName']
            print(f'[cfgen]\tfound distribution {ret} for {domain}')
    return ret


def distribution_present(record, domain, certificate):
    """Just a checker where to go"""
    # first we need to make some changes to the template, for example
    # inserting the distribution name and domain space.
    try:
        origin = domain + '.s3.amazonaws.com'
        data = yaml.safe_load(open('labs/templates/cloudfront.yaml', 'r'))
        data['DistributionConfig']['Aliases']['Items'][0] = domain
        data['DistributionConfig']['CallerReference'] = idgen.id_gen()
        data['DistributionConfig']['Comment'] = 'CloudFront for Static Websites'
        data['DistributionConfig']['Origins']['Items'][0]['Id'] = domain
        data['DistributionConfig']['Origins']['Items'][0]['DomainName'] = origin
        data['DistributionConfig']['DefaultCacheBehavior']['TargetOriginId'] = domain
        data['DistributionConfig']['ViewerCertificate']['ACMCertificateArn'] = acmgen.get_certs(certificate)
        data['DistributionConfig']['ViewerCertificate']['Certificate'] = acmgen.get_certs(certificate)
        print(f'[cfgen]\tgenerated data set for {origin}')
    except Exception as err:
        logging.error(f'An error occured: {err}')
    # now let's see if we need to create or update
    try:
        if list_distributions(record):
            update_distribution(data)
        else:
            create_distribution(data)
    except Exception as err:
        logging.error(f'An error occured: {err}')


def list_distributions(record):
    """Returns a boolean if the distribution is present"""
    try:
        print(f'[cfgen]\tfinding distribution for {record}')
        ret = False
        dists = _get_conn(service='cloudfront').list_distributions()
        for dist in dists['DistributionList']['Items']:
            origins = dist['Origins']['Items']
            for origin in origins:
                if record in origin['Id']:
                    print(f'[cfgen]\tfound distribution for {record}')
                    ret = True
        return ret
    except Exception as err:
        logging.error(f'An error occured: {err}')


def create_distribution(data):
    try:
        print('[cfgen]\tcreating distribution')
        _get_conn(service='cloudfront').create_distribution_with_tags(DistributionConfigWithTags=data)
        print('[cfgen]\tdistribution created with data set')
    except Exception as err:
        logging.error(f'An error occured: {err}')


def update_distribution(data):
    try:
        print('[cfgen]\tupdating distribution')
        #_get_conn(service='cloudfront').update_distribution(DistributionConfig=data)
        print('[cfgen]\tdistribution updated')
    except Exception as err:
        logging.error(f'An error occured: {err}')
