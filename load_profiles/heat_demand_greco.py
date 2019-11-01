# -*- coding: utf-8 -*-
"""
Creating heat demand profiles using the bdew method.

Installation requirements
-------------------------
This example requires at least version v0.1.4 of the oemof demandlib. Install
by:
    pip install 'demandlib>=0.1.4,<0.2'
Optional:
    pip install matplotlib

"""

import pandas as pd
import demandlib.bdew as bdew
import datetime
import os

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# read example temperature series

datapath = os.path.join(os.path.dirname(__file__), '/home/local/RL-INSTITUT/inia.steinbach/Dokumente/oemof/demandlib/demandlib/examples/example_data.csv')
temperature = pd.read_csv(datapath)["temperature"]


# The following dictionary is create by "workalendar"
# pip3 install workalendar
# >>> from workalendar.europe import Germany
# >>> cal = Germany()
# >>> holidays = dict(cal.holidays(2010))


def calculate_heat_demand(country, population, year):
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

    #annual_demand = bdew.calculate_annual_demand_households(self)
    # Create DataFrame for 2010
    demand = pd.DataFrame(
        index=pd.date_range(pd.datetime(2010, 1, 1, 0),
                            periods=8760, freq='H'))

    # calculate annual demand
    filename1='/home/local/RL-INSTITUT/inia.steinbach/rl-institut/04_Projekte/220_GRECO/03-Projektinhalte/AP4_High_Penetration_of_Photovoltaics/T4_all_Lastprofile/01_Household_profiles/Coal_consumption_residential.csv'
    filename2 ='/home/local/RL-INSTITUT/inia.steinbach/rl-institut/04_Projekte/220_GRECO/03-Projektinhalte/AP4_High_Penetration_of_Photovoltaics/T4_all_Lastprofile/01_Household_profiles/Gas_consumption_residential.csv'
    coal_demand= pd.read_csv(filename1, sep=';', index_col=0, header=1)
    gas_demand = pd.read_csv(filename2, sep=';', index_col=0, header=1)
    coal_demand[year] = pd.to_numeric(coal_demand[year], errors='coerce')
    gas_demand[year] = pd.to_numeric(gas_demand[year], errors='coerce')

    populations=pd.read_csv('/home/local/RL-INSTITUT/inia.steinbach/Dokumente/oemof/Lastprofile_GRECO/Data/EUROSTAT_population.csv', index_col=0, sep=';')
    total_heat_demand=(coal_demand.at[country, year] * 11.63 * 1000000) + (gas_demand.at[country, year] * 11.63 * 1000000)
    annual_heat_demand_per_population=(total_heat_demand/populations.at[country, 'Population']) * population


    # Multi family house (mfh: Mehrfamilienhaus)
    demand['mfh in MW/h'] = bdew.HeatBuilding(
        demand.index, holidays=holidays, temperature=temperature,
        shlp_type='MFH',
        building_class=2, wind_class=0, annual_heat_demand=annual_heat_demand_per_population,
        name='MFH').get_bdew_profile()

    if plt is not None:
        # Plot demand of building
        ax = demand.plot()
        ax.set_xlabel("Date")
        ax.set_ylabel("Heat demand in kW")
        plt.show()
    else:
        print('Annual consumption: \n{}'.format(demand.sum()))


if __name__ == '__main__':
    calculate_heat_demand(country='Germany', population=600, year='2013')
