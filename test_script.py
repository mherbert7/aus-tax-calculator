# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 20:56:16 2022

@author: Marcus
"""

import handler_classes as tax

scale_to_fortnight = 26

name = "Fred"
income = 76534 / 52
income_period = "weekly"
private_health = True
hecs = False
tfn_provided = True
resident_tax_status = "resident"
tax_free_threshold = "claimed"
full_medicare_levy_exemption = "not claimed"
half_medicare_levy_exemption = "not claimed"
financial_year = "2022-2023"


file_path = "config_files//schedule_1_withholding.yaml"

client = tax.individual(name, 
                        income, 
                        income_period, 
                        private_health, 
                        hecs, 
                        tfn_provided, 
                        resident_tax_status, 
                        tax_free_threshold, 
                        full_medicare_levy_exemption, 
                        half_medicare_levy_exemption)

tax_man = tax.ato(file_path)

tax_man.import_schedule_1()

final_val = tax_man.calculate_tax_withheld(financial_year, client)

print(final_val)
print(client.income_period)