from pvlib.location import Location
import pvlib.atmosphere
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
import matplotlib.pyplot as plt
import pvlib_CPVsystem as cpv
import pandas as pd
import numpy as np
import os
import pvlib

def create_PV_timeseries(lat, lon, weather, PV_setup=None, plot=True):

    """
    This function creates all PV time series for the three technologies for
    different orientations and saves each time series as csv.


    :param lat: latitude of the location
    :param lon: longitude of the location
    :param weather: weather Dataframe in the format of pvlib
    :param technology: dataframe with the technologies and the according orientations
                        with the columns: technology, surface_azimuth and
                        surface_tilt
    :return: None
    """

    if PV_setup is None:
        # read example PV_setup file
        datapath = os.path.join(os.path.dirname(__file__),
                                'Data/PV_setup.csv')
        PV_setup=pd.read_csv(datapath)

    technologies = PV_setup["technology"]

    for i in set(technologies):
        orientations= PV_setup.loc[(PV_setup["technology"] == i)]
        surface_azimuth=orientations['surface_azimuth']
        surface_tilt = orientations['surface_tilt']
        surface_tilt = pd.to_numeric(surface_tilt, errors='ignore')

        if i == "si":
            for i, row in orientations.iterrows():
                j = row['surface_azimuth']
                k = row['surface_tilt']
                k=pd.to_numeric(k, errors='ignore')
                if k == "optimal":
                    k=get_optimal_pv_angle(lat)

                timeseries=create_SI_timeseries(lat=lat, lon=lon, weather=weather, surface_azimuth=j, surface_tilt=k)
                timeseries.to_csv('Data/PV_feedin_SI_' + str(j) + '_' + str(k) + '.csv')

                if plot==True:
                    plt.plot(timeseries, label='si'+ str(j) + '_' + str(k))
                    plt.legend()

        elif i == "cpv":
            for i, row in orientations.iterrows():
                j = row['surface_azimuth']
                k = row['surface_tilt']
                k = pd.to_numeric(k, errors='ignore')
                if k == "optimal":
                    k=get_optimal_pv_angle(lat)
                timeseries=create_CPV_timeseries(lat, lon, weather, j, k)
                timeseries.to_csv('Data/PV_feedin_CPV_' + str(j) + '_' + str(k) + '.csv')

                if plot==True:
                    plt.plot(timeseries, label='cpv'+ str(j) + '_' + str(k))
                    plt.legend()

        elif i == "psi":
            for i, row in orientations.iterrows():
                j = row['surface_azimuth']
                k = row['surface_tilt']
                k = pd.to_numeric(k, errors='ignore')
                if k == "optimal":
                    k=get_optimal_pv_angle(lat)
                timeseries=create_SI_timeseries(lat, lon, weather, j, k)
                timeseries.to_csv('Data/PV_feedin_PSI_' + str(j) + '_' + str(k) + '.csv')

        else:
            print(i, 'is not in technologies. Please chose si, cpv or psi.')


    plt.show()

def get_optimal_pv_angle(lat):
    """ About 27° to 34° from ground in Germany.
    The pvlib uses tilt angles horizontal=90° and up=0°. Therefore 90° minus
    the angle from the horizontal.
    """
    return round(lat - 15)

def create_SI_timeseries(lat, lon, weather, surface_azimuth, surface_tilt):

    """
    creates an hourly time series for one SI module at a certain location and weather
    data for one year. The output time series is scaled to a capacity of ... MW

    :param location:
    :param weather:
    :param orientation:
    :return:
    """

    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
    cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
    system = PVSystem(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                          module_parameters=sandia_module,
                          inverter_parameters=cec_inverter)

    location=Location(latitude=lat, longitude=lon)

    mc = ModelChain(system, location)
    mc.run_model(times=weather.index, weather=weather)
    output=mc.dc
    return output['p_mp']


def create_CPV_timeseries(lat, lon, weather, surface_azimuth, surface_tilt):

    panel_location = pvlib.location.Location(latitude=lat, longitude=lon)

    module_params = {'gamma_ref': 5.524, 'mu_gamma': 0.003, 'I_L_ref': 0.96,
                     'I_o_ref': 0.00000000017, 'R_sh_ref': 5226,
                     'R_sh_0': 21000, 'R_sh_exp': 5.50, 'R_s': 0.01,
                     'alpha_sc': 0.00, 'EgRef': 3.91, 'irrad_ref': 1000,
                     'temp_ref': 25, 'cells_in_series': 12, 'eta_m': 0.32,
                     'alpha_absorption': 0.9}

    cpv_sys = cpv.StaticCPVSystem(surface_tilt=30, surface_azimuth=180,
                           module=None, module_parameters=module_params,
                           modules_per_string=1, strings_per_inverter=1,
                           inverter=None, inverter_parameters=None,
                           racking_model='insulated',
                           losses_parameters=None, name=None)

    spa = panel_location.get_solarposition(times=weather.index, pressure=None,
                                          temperature=weather['temp_air'])

    airmass = panel_location.get_airmass(weather.index)
    relative_airmass = airmass['airmass_relative'].fillna(0)

    # calculate AOI
    aoi_list = pd.Series(name='aoi')

    for index, row in spa.iterrows():
        aoi = pvlib.irradiance.aoi(surface_tilt=surface_tilt,
                                   surface_azimuth=surface_azimuth,
                                   solar_zenith=row['zenith'],
                                   solar_azimuth=row['azimuth'])
        aoi_list[index] = aoi

    weather['aoi'] = aoi_list

    celltemp = cpv_sys.pvsyst_celltemp(weather['ghi'],
                                    weather['temp_air'],
                                    weather['wind_speed'])

    (photocurrent, saturation_current, resistance_series,
     resistance_shunt, nNsVth) = (cpv_sys.calcparams_pvsyst(weather['dni'],
                                                         celltemp))

    cpv_sys.diode_params = (photocurrent, saturation_current, resistance_series,
                         resistance_shunt, nNsVth)

    cpv_sys.dc = cpv_sys.singlediode(photocurrent, saturation_current,
                               resistance_series,
                               resistance_shunt, nNsVth)

    estimation = cpv_sys.dc['p_mp']

    IscDNI_top = 0.96 / 1000

    thld_aoi = 61.978505569631494
    m_low_aoi = -2.716773886925838e-07
    m_high_aoi = -1.781998474992582e-05

    thld_am = 4.574231933073185
    m_low_am = 3.906372068620377e-06
    m_high_am = -3.0335768119184845e-05
    thld_temp = 50
    m_low_temp = 4.6781224141650075e-06
    m_high_temp = 0

    weight_am = 0.2
    weight_temp = 0.8

    uf_am = []
    for i, v in relative_airmass.items():
        uf_am.append(cpv.get_single_util_factor(v, thld_am,
                                                m_low_am / IscDNI_top,
                                                m_high_am / IscDNI_top))
    uf_temp = []
    for i, v in weather['temp_air'].items():
        uf_temp.append(cpv.get_single_util_factor(v, thld_temp,
                                                  m_low_temp / IscDNI_top,
                                                  m_high_temp / IscDNI_top))
    uf_aoi = []
    for i, v in weather['aoi'].items():
        uf_aoi.append(
            cpv.get_single_util_factor(v, thld_aoi, m_low_aoi / IscDNI_top,
                                       m_high_aoi / IscDNI_top))

    uf_aoi_ast = cpv.get_single_util_factor(0, thld_aoi,
                                            m_low_aoi / IscDNI_top,
                                            m_high_aoi / IscDNI_top)

    uf_aoi_norm = np.divide(uf_aoi, uf_aoi_ast)

    uf_am_temp = np.multiply(weight_am, uf_am) + np.multiply(weight_temp,
                                                             uf_temp)
    UF_global = np.multiply(uf_am_temp, uf_aoi_norm)

    return estimation * UF_global




#def create_PSI_timeseries(lat, lon, weather, surface_azimuth, surface_tilt):



if __name__ == '__main__':

    filename = os.path.abspath(
        "/home/local/RL-INSTITUT/inia.steinbach/rl-institut/04_Projekte/163_Open_FRED/03-Projektinhalte/AP2 Wetterdaten/open_FRED_TestWetterdaten_csv/fred_data_test_2016.csv")
    weather_df = pd.read_csv(filename, skiprows=range(1, 50), nrows=(5000),
                             index_col=0,
                             date_parser=lambda idx: pd.to_datetime(idx,
                                                                    utc=True))
    weather_df.index = pd.to_datetime(weather_df.index).tz_convert(
        'Europe/Berlin')

    create_PV_timeseries(lat=40.3, lon=5.4, weather=weather_df, PV_setup=None)