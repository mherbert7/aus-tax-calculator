# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 20:56:16 2022

@author: Marcus
"""

import the_classes as tax
import math

scale_to_fortnight = 26

name = "Fred"
income = 2000*26
private_health = True
hecs = False

ato_file_path = "ato_income_tax.yaml"

client = tax.individual(name, income, private_health, hecs)
tax_man = tax.ato(ato_file_path)

tax_man.import_ato_data()

medicare_levy = tax_man.calculate_medicare_levy_tax("2022-2023", client.get_salary())
hecs_tax = tax_man.calculate_hecs_tax("2022-2023", client.get_salary())
income_tax = tax_man.calculate_income_tax("2022-2023", client.get_salary())

print(medicare_levy)
print(hecs_tax)
print(income_tax)

final_val = tax_man.calculate_tax_withheld("2022-2023", client)/26
print(final_val)
