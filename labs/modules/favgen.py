#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""Basic favicon generator"""
import logging
try:
    from PIL import Image
except ModuleNotFoundError:
    logging.error('Pillow module is not installed.')

def image(input_img, bucket):
    types =  ['ico', 'png'] 
    for file_type in types:
        Image.open(input_img).save(f'{bucket}/favicon.{file_type}', sizes=[(32, 32)])
