#!/usr/bin/env python3
import random
import string


def id_gen(size=64, chars=string.hexdigits):
    """simple random token generator"""
    return ''.join(random.choice(chars) for _ in range(size))
