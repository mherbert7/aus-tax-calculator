# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 15:47:04 2022

@author: Marcus
"""

import yaml

class schedule_1_earnings:
    """
    A single earning threshold for a schedule 1 scale.
    """

    def __init__(self, threshold, earnings_dict):
        """
        Contain the data for a single earnings threshold.

        Parameters
        ----------
        threshold : float
            The earning threshold.
        earnings_dict : dict
            A dictionary that contains the earnings coefficients.
        """
        self.threshold = threshold
        self.a = earnings_dict["a"]
        self.b = earnings_dict["b"]
        

class schedule_1_scales:
    """
    A single scale in a schedule 1 financial year.
    """
    
    def __init__(self, scale_name, scale_dict):
        """
        Sort all the data for a given scale.

        Parameters
        ----------
        scale_name: str
            The name of the scale.
        scale_dict : dict
            A dictionary containing data for a single scale.
        """
        self.name = scale_name
        self.tfn_provided = scale_dict["tfn_provided"]
        self.resident_tax_status = scale_dict["resident_tax_status"]
        self.tax_free_threshold = scale_dict["tax_free_threshold"]
        self.full_medicare_levy_exemption = scale_dict[
                                                "full_medicare_levy_exemption"]
        self.half_medicare_levy_exemption = scale_dict[
                                                "half_medicare_levy_exemption"]
        self.mask = [self.tfn_provided, 
                     self.resident_tax_status,
                     self.tax_free_threshold,
                     self.full_medicare_levy_exemption,
                     self.half_medicare_levy_exemption]
        
        self.weekly_earnings_thresholds = {}
        
        earnings_dict = scale_dict["weekly_earnings_less_than_thresholds"]
        for threshold in earnings_dict:
            self.weekly_earnings_thresholds[threshold] = \
                    schedule_1_earnings(threshold, earnings_dict[threshold])


class schedule_1_fy:
    """
    A single schedule 1 financial year.
    """

    def __init__(self, fy_dict):
        """
        Sort all the data for a given schedule 1 financial year.

        Parameters
        ----------
        fy_dict : dict
            The dictionary containing all the data from a given financial year.
        """
        self.document = fy_dict["document"]
        self.fy = fy_dict["financial_year"]
        self.same_as_other_fy = fy_dict["same_as_other_financial_year"]
        self.fy_for_comparison = fy_dict["financial_year_for_comparison"]
        self.scales = {}
        
        for scale in fy_dict["scales"]:
            self.scales[scale] = schedule_1_scales(scale, 
                                                   fy_dict["scales"][scale])
        

class schedule_1:
    """
    A class to handle schedule 1 data (income and medicare levy).
    """
    
    def __init__(self, file_path):
        """
        Handle the importing of data from schedule 1.

        Parameters
        ----------
        file_path : str
            The path to the YAML file that contains schedule 1 data.
        """
        self.file_path = file_path
        self._import_dict = {}
        self.import_successful = False
        self.financial_years = []
        
        
    def import_data(self):
        """
        Import the data from a file.
        """
        try:
            file = open(self.file_path, "r")
            self._import_dict = yaml.safe_load(file)
            self.financial_years = []
            
            
            for fy in self._import_dict:
                temp_fy = schedule_1_fy(self._import_dict[fy])
                self.financial_years += [temp_fy]
                
            self.import_successful = True
        except Exception as e:
            print("Unable to open the tax rates file. Error:", e)
            self.import_successful = False  


class ato:
    """
    A class to load the details from the ATO.
    """
    
    def __init__(self, schedule_1_path, schedule_8_path=None):
        """
        The init function for this class.

        Parameters
        ----------
        schedule_1_path : str
            The path to the file that contains the schedule 1 data.
        schedule_8_path : str
            The path to the file that contains the schedule 8 data.
        """
        self.schedule_1_path = schedule_1_path
        self.schedule_1 = None
        self.schedule_8_path = schedule_8_path
        self.schedule_8 = None
        
        self._financial_year_dict = {}
        self._import_successful = False
        
        self.scale_1_mask = [True, 
                             "resident", 
                             "not claimed", 
                             "not claimed", 
                             "not claimed"]
        
        self.scale_2_mask = [True,
                             "resident",
                             "claimed",
                             "not claimed",
                             "not claimed"]
        
        
    def import_schedule_1(self):
        """
        Import the schedule 1 data.
        """
        self.schedule_1 = schedule_1(self.schedule_1_path)
        self.schedule_1.import_data()
        
        
    def ignore_cents_add_99(self, value):
        """
        A simple function to perform a frequent task of ignoring cents and 
        adding 99 cents back on to a value.

        Parameters
        ----------
        value : float
            The value to remove cents from, and add 99 to.

        Returns
        -------
        float
            The adjusted value.
        """
        new_value = int(value) + 0.99
        return new_value
        
        
    def calculate_weekly_earnings(self, 
                           income, 
                           current_period, 
                           allowances=0):
        """
        Convert the income from one period to weekly.

        Parameters
        ----------
        income : float
            The current income.
        current_period : str
            Valid options are "annual", "quarterly", "monthly", "fortnightly"
            and "weekly".
        new_period : str
            Valid options are "annual", "quarterly", "monthly", "fortnightly"
            and "weekly".
        allowances : float
            Any additional allowances that may be subject to withholding.

        Returns
        -------
        float
            Earnings
        """
        earnings = 0
        temp = 0
        
        if(current_period == "annual"):
            temp = (income + allowances) / 52 
            
        elif(current_period == "quarterly"):
            temp = (income + allowances) / 13
            
        elif(current_period == "monthly"):
            temp = income + allowances
            #TODO: This won't really work properly due to floating point issues
            #Need to update all numbers to Decimal or something.
            if((((int(temp*100)) / 100) - int(temp)) == 0.33):
                temp += 0.01
                
            temp = (temp * 3) / 13
            
        elif(current_period == "fortnightly"):
            temp = income / 26
            
        elif(current_period == "weekly"):
            temp = income
            
        earnings = self.ignore_cents_add_99(temp)
        
        return earnings
            
            
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
            Tax to be withheld, on a weekly basis.
        """
        fy = financial_year
        client = the_individual
        
        tax = 0

        for item in self.schedule_1.financial_years:
            if(item.fy == financial_year):
                for scale in item.scales:
                    if(client.income_mask == item.scales[scale].mask):
                        sc = item.scales[scale]
                        earnings = sc.weekly_earnings_thresholds
                        weekly_income = int(client.get_salary()/52) + 0.99
                        thresholds = (i for i in earnings if weekly_income < i)
                        threshold = min(thresholds)
                        a = earnings[threshold].a
                        b = earnings[threshold].b
                        tax = round(a * weekly_income - b)
                        break
                    
        print("The tax is:", tax, "weekly")
        print("The tax is:", tax*2, "fortnightly")
        print("The tax is:", tax*52, "over 52 weeks")
        
    
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
                 has_hecs,
                 tfn_provided,
                 resident_tax_status,
                 tax_free_threshold,
                 full_medicare_levy_exemption,
                 half_medicare_levy_exemption):
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
        
        self.tfn_provided = tfn_provided
        self.resident_tax_status = resident_tax_status
        self.tax_free_threshold = tax_free_threshold
        self.full_medicare_levy_exemption = full_medicare_levy_exemption
        self.half_medicare_levy_exemption = half_medicare_levy_exemption
        
        self.income_mask = [self.tfn_provided,
                            self.resident_tax_status,
                            self.tax_free_threshold,
                            self.full_medicare_levy_exemption,
                            self.half_medicare_levy_exemption]
        
        
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