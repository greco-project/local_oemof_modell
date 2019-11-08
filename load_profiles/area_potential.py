# -*- coding: utf-8 -*-
"""

calculating the available area potential for PV-modules on the rooftop and facades

"""

import matplotlib.pyplot as plt
import pandas as pd

def calculate_area_potential(population):

    """
    calculates the area potential of the rooftop, south and east+west facades
    for a given population

    :param population:
    :return: number of storeys of each house, available area for flatroof,
            available area for gableroof, available south facade,
            available east+west facades
    """

    storeys= population/24/5

    flatroof_area = 1232 * 5
    gableroof_area = (1232 * 5 / 100) * 70
    total_floor_area = 1232 *5 * storeys

    if storeys > 3:
        used_storeys = storeys - 3
#        south_facade = (56 * 3 * used_storeys - (56 * 3 * used_storeys / 100) *30) * 5
#        eastwest_facade = (22 * 3 * 2 * used_storeys - (120*4 / 100) *4) *5
        south_facade = 56 * 3 * used_storeys * 5
        eastwest_facade = 22 * 3 * 2 * used_storeys *5

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
    plot_facade_potential()