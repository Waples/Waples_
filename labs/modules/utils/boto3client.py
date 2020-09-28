#!/usr/bin/env python3
"""
Represents a boto3 Client for the given service.
"""

# import python libs
import logging

try:
    import boto3
except ImportError:
    logging.error('Boto3 library is not installed.')

def _get_conn(service, region='eu-west-1'):
    """Return the boto3 client for the given service."""
    return boto3.client(service_name=service, region_name=region)
