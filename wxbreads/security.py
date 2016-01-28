#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from Crypto.Cipher import AES


def encrypt(text, key, iv):
    return AES.new(key, AES.MODE_CFB, iv).encrypt(text)


def decrypt(text, key, iv):
    return AES.new(key, AES.MODE_CFB, iv).decrypt(text)
