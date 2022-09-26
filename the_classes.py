# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 15:47:04 2022

@author: Marcus
"""

import yaml
import math

class financial_year_data:
    """
    A class to handle data for a single financial year.
    """
    
    def __init__(self, fy_dict):
        """
        Initialise the financial year object.

        Parameters
        ----------
        fy_dict : dict
            The dictionary 
        """
        self._fy_dict = fy_dict
        
        self.financial_year = fy_dict["financial_year"]
        self.income_tax_bands = fy_dict["income_tax_bands"]
        self.medicare_levy = fy_dict["medicare_levy"]
        self.medicare_levy_surcharge = fy_dict["medicare_levy_surcharge"]
        self.hecs = fy_dict["HECS"]


class ato:
    """
    A class to load the details from the ATO.
    """
    
    def __init__(self, tax_rates_file_path):
        """
        The init function for this class.

        Parameters
        ----------
        tax_rates_file_path : string
            The path to the file that contains the tax rates.
        """
        self._tax_rates_file_path = tax_rates_file_path
        self._financial_year_dict = {}
        self._import_successful = False
        
    
    def import_ato_data(self):
        """
        Import the ATO data from a file.
        """
        try:
            tax_file = open(self._tax_rates_file_path, "r")
            self._financial_year_dict = yaml.safe_load(tax_file)
            self.financial_years = []
            
            for fy in self._financial_year_dict:
                temp_fy = financial_year_data(self._financial_year_dict[fy])
                self.financial_years += [temp_fy]
                
            self._import_successful = True
        except Exception as e:
            print("Unable to open the tax rates file. Error:", e)
            self._import_successful = False
            
            
    def calculate_tax_withheld(self, financial_year, the_individual):
        """
        A function to calculate the tax withheld for an individual in a given
        financial year.

        Parameters
        ----------
        financial_year : str
            The financial year to calculate the tax withheld for. For example,
            "2022-2023" for that financial year.
        the_individual : individual
            An individual object.

        Returns
        -------
        float
            total_tax_withheld
        """
        fy = financial_year
        client = the_individual
        
        total_tax = 0
        
        medicare_levy = self.calculate_medicare_levy_tax(fy, client.get_salary())
        total_tax += medicare_levy[0]
        
        income_tax = self.calculate_income_tax(fy, client.get_salary())
        total_tax += income_tax[0]
        
        if(client.get_has_hecs()):
            hecs_tax = self.calculate_hecs_tax(fy, client.get_salary())
            total_tax += hecs_tax[0]
        
        return total_tax
        
    
    def search_for_income_band(self, tax_data, taxable_income):
        """
        Search for the appropriate income band to find the right tax rate.

        Parameters
        ----------
        tax_data : dict
            A dict of the tax data (medicare levy, HECS, etc)
        taxable_income : float
            The taxable income used to find the right income band.

        Returns
        -------
        tuple of str, float
            (The name of the tax band, the tax rate in the given band)

        """        
        tax_band = ""
        tax_rate = 0
        
        for band in tax_data:
            if((taxable_income >= tax_data[band]["min_income"]) and \
               (taxable_income <= tax_data[band]["max_income"])):
                
                tax_band = band
                tax_rate = tax_data[band]["tax_rate"]
                break
            
        return (tax_band, tax_rate)
    
    
    def search_for_lower_income_bands(self, tax_data, taxable_income):
        """
        Search for the income bands that are below the correct band.

        Parameters
        ----------
        tax_data : dict
            A dict of the tax data (medicare levy, HECS, etc)
        taxable_income : float
            The taxable income used to find the income bands.

        Returns
        -------
        dict
            A dict of the lower income bands and their rates.

        """        
        tax_bands_and_rates = {}
        
        for band in tax_data:
            if(taxable_income > tax_data[band]["max_income"]):
                
                tax_bands_and_rates[band] = tax_data[band]
            
        return tax_bands_and_rates
        
        
    def calculate_medicare_levy_tax(self, financial_year, taxable_income):
        """
        Calculate the medicare levy tax from the taxable income.

        Parameters
        ----------
        financial_year : str
            The financial year to calculate the tax withheld for. For example,
            "2022-2023" for that financial year. 
        taxable_income : float
            The taxable income used to calculate the medicare levy tax.

        Returns
        -------
        tuple of float, str, float
            (tax value, tax rate, tax band)
        """
        for fy in self.financial_years:
            if(fy.financial_year == financial_year):
                tax_data = fy
        
        band, tax_rate = self.search_for_income_band(
                                tax_data.medicare_levy, taxable_income)
        
        tax_value = taxable_income * tax_rate
        
        return (tax_value, tax_rate, band)
    
    
    def calculate_hecs_tax(self, financial_year, assessable_income):
        """
        Calculate the HECS tax from the assessable income.

        Parameters
        ----------
        financial_year : str
            The financial year to calculate the tax withheld for. For example,
            "2022-2023" for that financial year. 
        assessable_income : float
            The assessable income used to calculate the HECS tax.

        Returns
        -------
        tuple of float, str, float
            (tax value, tax rate, tax band)
        """
        for fy in self.financial_years:
            if(fy.financial_year == financial_year):
                tax_data = fy
        
        band, tax_rate = self.search_for_income_band(
                                tax_data.hecs, assessable_income)
        
        tax_value = assessable_income * tax_rate
        
        return (tax_value, tax_rate, band)
    
    
    def calculate_income_tax(self, financial_year, taxable_income):
        """
        Calculate the income tax from the taxable income.

        Parameters
        ----------
        financial_year : str
            The financial year to calculate the tax withheld for. For example,
            "2022-2023" for that financial year. 
        taxable_income : float
            The taxable income to calculate the income tax.

        Returns
        -------
        tuple of float, float, list
            (income tax value, marginal tax rate, tax values from each band)
        """
        for fy in self.financial_years:
            if(fy.financial_year == financial_year):
                tax_data = fy
        
        #Get the taxed value from the marginal band
        band, marginal_rate = self.search_for_income_band(
                                        tax_data.income_tax_bands, 
                                        taxable_income)
        
        non_assessed_income = tax_data.income_tax_bands[band]["min_income"]
        marginal_income = taxable_income - non_assessed_income
        marginal_tax_value = marginal_income * marginal_rate
        
        #Get the taxed value from the bands below the marginal band
        lower_tax_bands = self.search_for_lower_income_bands(
                                                tax_data.income_tax_bands, 
                                                taxable_income)
        
        tax_values = [marginal_tax_value]
        total_tax_value = marginal_tax_value
        
        for band in lower_tax_bands:
            taxed_income = lower_tax_bands[band]["max_income"] + 1 - \
                            lower_tax_bands[band]["min_income"]
            tax_value = taxed_income * lower_tax_bands[band]["tax_rate"]
            total_tax_value += tax_value
            
            tax_values += [tax_value]
        
        return (total_tax_value, marginal_rate, tax_values)


class individual:
    """
    A class to contain an individual's information.    
    """
    
    def __init__(self,
                 name,
                 annual_salary, 
                 has_private_health, 
                 has_hecs):
        """
        The init function for this class.

        Parameters
        ----------
        name : str
            The name of the individual.
        annual_salary : float
            Annual salary in AUD. I made it float to allow for a salary that 
            specifies cents.
        has_private_health : bool
            If the individual has private health insurance for the entire 
            financial year, then this is true. If not, then false.
        has_hecs : bool
            If the individual has a HECS debt, then this is true. False if not.
        """
        self.name = name
        
        self._salary = annual_salary
        self._has_private_health = has_private_health
        self._has_hecs = has_hecs
        
        self._medicare_levy_tax_rate = 0
        self._medicare_levy_tax = 0
        
        self._hecs_tax_rate = 0
        self._hecs_tax = 0
        
        self._marginal_tax_rate = 0
        self._income_tax = 0
        
        
    def get_salary(self):
        """
        A function to return the individual's salary.

        Returns
        -------
        float
            The individual's salary.
        """
        return self._salary
    
    
    def set_salary(self, salary):
        """
        Sets the individual's new salary.

        Parameters
        ----------
        salary : float
            The individual's new salary.
        """
        self._salary = salary
        
        
    def get_has_private_health(self):
        """
        A function to return whether the individual has private health cover.

        Returns
        -------
        bool
            True if the individual has private health. False if not.
        """
        return self._has_private_health
    
    
    def set_has_private_health(self, has_private_health):
        """
        A function to set the individual's private health status.

        Parameters
        ----------
        has_private_health : bool
            True if the individual has private health cover for the entire
            financial year. False if not.
        """
        self._has_private_health = has_private_health
        
        
    def get_has_hecs(self):
        """
        A function to return whether the individual has a HECS debt or not.

        Returns
        -------
        bool
            True if they have a HECS debt. False if not.
        """
        return self._has_hecs
    
        
    def set_has_hecs(self, has_hecs):
        """
        A function to set the individual's HECS debt status.

        Parameters
        ----------
        has_hecs : bool
            True if they have a HECS debt. False if not. 
        """
        self._has_hecs = has_hecs