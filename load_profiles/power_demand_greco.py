  # -*- coding: utf-8 -*-
"""
Creating power demand profiles using bdew profiles.

Installation requirements
-------------------------
This example requires at least version v0.1.4 of the oemof demandlib. Install
by:
    pip install 'demandlib>=0.1.4,<0.2'
Optional:
    pip install matplotlib

"""

import datetime
import demandlib.bdew as bdew
import demandlib.particular_profiles as profiles
from datetime import time as settime
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

import os
import pandas as pd

# The following dictionary is create by "workalendar"
# pip3 install workalendar
# >>> from workalendar.europe import Germany
# >>> cal = Germany()
# >>> holidays = dict(cal.holidays(2010))

holidays = {
    datetime.date(2010, 5, 24): 'Whit Monday',
    datetime.date(2010, 4, 5): 'Easter Monday',
    datetime.date(2010, 5, 13): 'Ascension Thursday',
    datetime.date(2010, 1, 1): 'New year',
    datetime.date(2010, 10, 3): 'Day of German Unity',
    datetime.date(2010, 12, 25): 'Christmas Day',
    datetime.date(2010, 5, 1): 'Labour Day',
    datetime.date(2010, 4, 2): 'Good Friday',
    datetime.date(2010, 12, 26): 'Second Christmas Day'}



def calculate_power_demand(country, population, year):

    filename='/home/local/RL-INSTITUT/inia.steinbach/Dokumente/oemof/Lastprofile_GRECO/Data/Electricity_consumption_residential.csv'
    powerstat= pd.read_csv(filename, sep=';', index_col=0)

    populations=pd.read_csv('/home/local/RL-INSTITUT/inia.steinbach/Dokumente/oemof/Lastprofile_GRECO/Data/EUROSTAT_population.csv', index_col=0, sep=';')
    national_energyconsumption=powerstat.at[country, year] * 11.63 * 1000000
    annual_demand_per_population=(national_energyconsumption / populations.at[country, 'Population']) * population


    ann_el_demand_h0 = {
        'h0': annual_demand_per_population}

    # read standard load profiles
    year= int(year)

    e_slp = bdew.ElecSlp(year, holidays=holidays)

    load_profile_h0=e_slp.create_bdew_load_profiles(dt_index=e_slp.date_time_index, slp_types=['h0'], holidays=None)

    # multiply given annual demand with timeseries
    load_elec_demand=e_slp.all_load_profiles(time_df=e_slp.date_time_index, holidays=None)
    elec_demand = e_slp.get_profile(ann_el_demand_h0)
    ilp = profiles.IndustrialLoadProfile(e_slp.date_time_index,
                                         holidays=holidays)

    # Change scaling factors
    elec_demand['h0'] = ilp.simple_profile(
        ann_el_demand_h0['h0'],
        profile_factors={'week': {'day': 1.0, 'night': 0.8},
                         'weekend': {'day': 0.8, 'night': 0.6}})

    # Resample 15-minute values to hourly values.
    elec_demand = elec_demand.resample('H').mean()
    print("Annual electricity demand:", elec_demand.sum())

    if plt is not None:
        # Plot demand
        ax = elec_demand.plot()
        ax.set_xlabel("Date")
        ax.set_ylabel("Power demand")
        plt.show()


if __name__ == '__main__':
    calculate_power_demand(country='Germany', population=600, year='2011')
