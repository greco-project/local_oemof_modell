# -*- coding: utf-8 -*-
"""

calculating the available area potential for PV-modules on the rooftop and facades

"""

import matplotlib.pyplot as plt
import pandas as pd
import os

def calculate_area_potential(population):

    """
    calculates the area potential of the rooftop, south and east+west facades
    for a given population

    :param population:
    :return: number of storeys of each house, available area for flatroof,
            available area for gableroof, available south facade,
            available east+west facades
    """
    # read example temperature series
    datapath = os.path.join(os.path.dirname(__file__),
                            'Data/building_parameters.csv')
    bp = pd.read_csv(datapath, index_col=0)
    bp=bp.T
    population_per_storey=bp.iloc[0]['population per storey']
    number_houses = bp.iloc[0]['number of houses']
    total_floor_area = bp.iloc[0]['total storey area']
    length_south_facade = bp.iloc[0]['length south facade']
    length_eastwest_facade = bp.iloc[0]['length eastwest facade']
    hight_per_storey=bp.iloc[0]['hight storey']

    storeys= population/population_per_storey/number_houses

    flatroof_area = total_floor_area * number_houses
    gableroof_area = (total_floor_area * number_houses / 100) * 70
    total_floor_area = total_floor_area *number_houses * storeys

    if storeys > 3:
        used_storeys = storeys - 3
#        south_facade = (56 * 3 * used_storeys - (56 * 3 * used_storeys / 100) *30) * 5
#        eastwest_facade = (22 * 3 * 2 * used_storeys - (120*4 / 100) *4) *5
        south_facade = length_south_facade * hight_per_storey * used_storeys * number_houses
        eastwest_facade = length_eastwest_facade * hight_per_storey * 2 * used_storeys *number_houses

        used_south_facade = south_facade/100 * 50
        used_eastwest_facade = eastwest_facade/100 * 80
    else:
        used_south_facade = 0
        used_eastwest_facade = 0

    print("number of storys:", storeys, "\n"
        "flat rooftop area:", flatroof_area, "\n"
            "gable rooftop area facing south:", gableroof_area, "\n"
          "south facade area:", used_south_facade, "\n"
          "eastwest facade area:", used_eastwest_facade, "\n")

    return(storeys, used_south_facade, used_eastwest_facade, total_floor_area)

def plot_facade_potential():

    population = range(0, 1300, 120)
    storeys = {}
    south = {}
    eastwest = {}
    total_floor = {}

    for i in population:
        storeys[i], south[i], eastwest[i], total_floor[i] = \
            calculate_area_potential(population=i)

    st = pd.DataFrame(list(storeys.items()))
    st.columns = ['population', 'storeys']
    st.set_index('population', inplace=True)
    s = pd.DataFrame(list(south.items()))
    s.columns = ['population', 'south_facade']
    s.set_index('population', inplace=True)
    e = pd.DataFrame(list(eastwest.items()))
    e.columns = ['population', 'eastwest_facade']
    e.set_index('population', inplace=True)
    t = pd.DataFrame(list(total_floor.items()))
    t.columns = ['population', 'total_floor_area']
    t.set_index('population', inplace=True)

    area = pd.concat([st, s, e, t], axis=1)

    plt.plot(area['storeys'],
             area['south_facade'] / area['total_floor_area'] * 100,
             label='south_facade')
    plt.plot(area['storeys'],
             area['eastwest_facade'] / area['total_floor_area'] * 100,
             label='eastwest_facades')
    plt.ylabel('fraction of used facade to the total floor area')
    plt.xlabel('number of floors')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    calculate_area_potential(population=600)
    #plot_facade_potential()