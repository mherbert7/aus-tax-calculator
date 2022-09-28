# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 11:42:25 2022

@author: Marcus
"""

import handler_classes as hc

file_path = "config_files//schedule_1_withholding.yaml"

skej1 = hc.schedule_1(file_path)
skej1.import_data()