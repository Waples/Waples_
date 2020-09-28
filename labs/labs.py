#!/usr/bin/env python3
"""
Wrapper script to generate the static s3 website for `labs`.
"""
# import python libs
import logging
import os
import shutil
import webbrowser
from sys import argv

# import custom modules
try:
    from modules import acmgen
    from modules import cfgen
    from modules import favgen
    from modules import gen53
    from modules import s3gen
except ImportError as err:
    logging.error(f'One or more custom modules are not installed\n{err}.')

# TODO: add some protection on this...
if argv[1:2]:
    RECORD = argv[1:2][0]
else:
    RECORD = 'labs'

REGION = 'eu-west-1'
DOMAIN = 'freyrsvin.nl'
FQDN = RECORD + '.' + DOMAIN
WEBSITE = 'source/website/'
UPLOAD = 'bucket/'

# pylint: disable=W1203,C0103

# introduction
print(f'\n\tlabs !\n\tProvisioning static S3 website for {FQDN}.\n')

# create the UPLOAD dir and copy source/website/ items to that dir
if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD)
for item in os.listdir(WEBSITE):
    shutil.copyfile(WEBSITE + item, UPLOAD + item)

# generate favicon
try:
    favgen.image('source/favicon.png', UPLOAD)
except FileNotFoundError as err:
    logging.error(f'[favicon] General error: {err}')

# generate an ACM certificate for the *.{DOMAIN}
acmgen.certificate_present(FQDN, DOMAIN)

# generate s3 FQDN (as website with public viewing) if not already there
s3gen.create(FQDN)

# sync to s3 FQDN
s3gen.sync(FQDN, UPLOAD)

# put cloudfront in front of the static website.
cfgen.distribution_present(RECORD, FQDN, f'*.{DOMAIN}')

# generate route53 RecordSet, if not already available.
gen53.record_set_present(DOMAIN, RECORD, REGION)

# remove the upload dir and other cleanup
shutil.rmtree(UPLOAD, ignore_errors=True)

# open the {FQDN} in the browser.
print(f'\n\tOpening {FQDN} in your browser.')
webbrowser.open_new(FQDN)

print('\tCloudFront takes about 15 minutes to be fully enabled, give it some time.')
