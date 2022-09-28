# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 20:56:16 2022

@author: Marcus
"""

import handler_classes as tax

scale_to_fortnight = 26

name = "Fred"
income = 76534
private_health = True
hecs = False
tfn_provided = True
resident_tax_status = "resident"
tax_free_threshold = "claimed"


file_path = "config_files//schedule_1_withholding.yaml"

client = tax.individual(name, income, private_health, hecs, True, "resident", "claimed", "not claimed", "not claimed")
tax_man = tax.ato(file_path)

tax_man.import_schedule_1()

final_val = tax_man.calculate_tax_withheld("2022-2023", client)
print(final_val)
