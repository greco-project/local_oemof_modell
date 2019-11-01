'''
This script has a second model where the idea for a big storage acting as a grid to simulate NZEB will be implemented.
'''
# import necessary libraries

import logging
import oemof
import pandas as pd

from oemof.solph import (Sink, Source, Bus, Flow, EnergySystem, Investment, Model)
from oemof.solph.components import GenericStorage
from oemof.outputlib import processing, views
import pprint as pp

from oemof.tools import economics

oemof.tools.logger.define_logging(logfile='oemof example.log', screen_level=logging.INFO, file_level=logging.DEBUG)

# Creating the energy system

date_time_index = pd.date_range('1/1/2018', periods=24 * 365, freq='H')

es = EnergySystem(timeindex=date_time_index)

filename = 'data_timeseries.csv'
data = pd.read_csv(filename, sep=",")

logging.info('Energy system created and initialized')

# Creating the necessary buses

elbus = Bus(label='mainbus')
elbus2 = Bus(label='pvtobatbus')

logging.info('Necessary buses for the system created')

# Now creating the necessary components for the system

epc_pv = economics.annuity(capex=1000, n=20, wacc=0.05)
epc_storage = economics.annuity(capex=1000, n=20, wacc=0.05)

pv = Source(label='pv', outputs={elbus2: Flow(actual_value=data['pv'], nominal_value=None,
                                              fixed=True, investment=Investment(ep_costs=epc_pv))})

demand_el = Sink(label='demand_el', inputs={elbus: Flow(nominal_value=1, actual_value=data['demand_el'], fixed=False)})
excess_el = Sink(label='excess_el', inputs={elbus: Flow(variable_costs=0)})
shortage_el = Source(label='shortage_el', outputs={elbus: Flow(variable_costs=1e6)})

