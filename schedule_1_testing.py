# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 19:40:24 2022

@author: Marcus
"""

import yaml

#filename = "ato_income_tax.yaml"
filename = "schedule_1_withholding.yaml"

file = open(filename, "r")

file_read = yaml.safe_load(file)

#print(file_read)

earnings = file_read["financial_year_2022_2023"]["scale_1"]["weekly_earnings_thresholds"]
print(earnings)