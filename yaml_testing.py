# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 14:55:05 2022

@author: Marcus
"""

import yaml

filename = "ato_income_tax.yaml"

file = open(filename, "r")

file_read = yaml.safe_load(file)

print(file_read)