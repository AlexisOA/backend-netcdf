from siphon.catalog import *
import xarray as xr
import numpy as np
import netCDF4
from netCDF4 import num2date, date2num, date2index
import pandas as pd
import threddsclient
import os
from django.conf import settings
import json
from datetime import datetime, timedelta

class AutonomousSystems:

    def get_dataset_glider(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        dataset = {}
        USV_DATA = []
        data = {}
        data_dataset = {}
        data_coordinates = {}
        coordinates = {}

        for coord in list(ds.coords):
            if "GPS" in coord or "PRES" in coord: continue
            if coord == 'TIME':
                my_date = np.array(
                    [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(ds.TIME.values, ds.TIME.units)])
                data_coordinates[coord.lower().capitalize()] = my_date
                continue
            data_coordinates[coord.lower().capitalize()] = ds.variables[coord].values.flatten()
        data["coordinates"] = data_coordinates
        # USV_DATA.append(coordinates)
        variables_available = ["PSAL", "TEMP", "CNDC", "PRES", "CHLA"]
        # data["names"] = names
        data_dataset["names"] = []
        data_dataset["values"] = []
        data_dataset["units"] = []
        for var in list(ds.variables):
            if var in variables_available:
                dset = np.float64(np.nan_to_num(ds.variables[var].values))
                data_dataset["names"].append(var)
                data_dataset["values"].append(dset.flatten())
                data_dataset["units"].append(ds.variables[var].attrs['units'])
        data["data"] = data_dataset
        USV_DATA.append(data)
        dataset["USV_DATA"] = USV_DATA
        return dataset

    def get_dataset_glider_without_nan(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        dataset = {}
        USV_DATA = []
        data = {}
        data_dataset = {}
        data_coordinates = {}
        usv_data_dict = {}

        date = ds.TIME_GPS.values
        latitude = ds.LATITUDE_GPS.values
        longitude = ds.LONGITUDE_GPS.values
        indices = np.where(
            # (ds.TIME.values is not None) & (ds.LATITUDE.values is not None) & (ds.LONGITUDE.values is not None)
            (~np.isnan(date)) & (~np.isnan(latitude)) & (~np.isnan(longitude))
        )

        data_coordinates["Time"] = np.array(
            [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(date[indices], ds.TIME_GPS.units)])
        data_coordinates["Latitude"] = latitude[indices]
        data_coordinates["Longitude"] = longitude[indices]

        data["coordinates"] = data_coordinates

        variables_available = ["PSAL", "TEMP", "CNDC", "PRES", "CHLA"]
        # data["names"] = names
        data_dataset["names"] = []
        data_dataset["values"] = []
        data_dataset["units"] = []
        for var in list(ds.variables):
            if var in variables_available:
                # dset = np.nan_to_num(ds.variables[var].values)
                data_dataset["names"].append(var)
                # data_dataset["values"].append(dset[indices])
                # data_dataset["units"].append(ds.variables[var].attrs['units'])
        dset = np.nan_to_num(ds.variables[variables_available[0]].values)
        data_dataset["values"].append(dset[indices])
        data_dataset["units"].append(ds.variables[variables_available[0]].attrs['units'])
        data["data"] = data_dataset
        USV_DATA.append(data)
        dataset["USV_DATA"] = USV_DATA
        return dataset

    def get_dataset_glider_without_nan_2(self, url):
        print("entrando")
        ds = xr.open_dataset(url, decode_times=False)
        dataset = {}
        USV_DATA = []
        data = {}
        data_dataset = {}
        data_coordinates = {}
        usv_data_dict = {}

        date = np.delete(ds.TIME_GPS.values, 0, axis=None)
        latitude = np.delete(ds.LATITUDE_GPS.values, 0, axis=None)
        longitude = np.delete(ds.LONGITUDE_GPS.values, 0, axis=None)
        indices = np.where(
            # (ds.TIME.values is not None) & (ds.LATITUDE.values is not None) & (ds.LONGITUDE.values is not None)
            (~np.isnan(date)) & (~np.isnan(latitude)) & (~np.isnan(longitude))
        )

        data_coordinates["Time"] = np.array(
            [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(date[indices], ds.TIME.units)])
        # data_coordinates["Latitude"] = latitude[indices]
        # data_coordinates["Longitude"] = longitude[indices]

        # data["coordinates"] = data_coordinates

        variables_available = ["PSAL", "TEMP", "CNDC", "PRES", "CHLA"]
        # data["names"] = names
        data_dataset["names"] = []
        data_dataset["values"] = []
        data_dataset["units"] = []
        for var in list(ds.variables):
            if var in variables_available:
                # dset = np.nan_to_num(ds.variables[var].values)
                data_dataset["names"].append(var)
                # data_dataset["values"].append(dset[indices])
                # data_dataset["units"].append(ds.variables[var].attrs['units'])
        dset = np.nan_to_num(ds.variables[variables_available[0]].values)
        # data_dataset["values"].append(dset[indices])
        data_dataset["units"].append(ds.variables[variables_available[0]].attrs['units'])

        data_coordinates['coordinates'] = [[i, j, k] for i, j, k in
                                           zip(latitude[indices], longitude[indices], dset[indices]) if
                                           not (pd.isnull(i) or pd.isnull(j))]
        data["coordinates"] = data_coordinates
        data["data"] = data_dataset
        USV_DATA.append(data)
        dataset["USV_DATA"] = USV_DATA
        return dataset

    def get_dataset_glider_coordinates(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        data = {}
        dataset = {}
        USV_DATA = []
        coordinates = {}
        data_dataset = {}
        date = np.delete(ds.TIME_GPS.values, 0, axis=None)
        latitude = np.delete(ds.LATITUDE_GPS.values, 0, axis=None)
        longitude = np.delete(ds.LONGITUDE_GPS.values, 0, axis=None)
        # date =ds.TIME_GPS.values
        # latitude = ds.LATITUDE_GPS.values
        # longitude = ds.LONGITUDE_GPS.values
        indices = np.where(
            (~np.isnan(date)) & (~np.isnan(latitude)) & (~np.isnan(longitude))
        )

        date = date[indices]
        latitude = latitude[indices]
        longitude = longitude[indices]

        date_all = np.array(
            [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(date, ds.TIME.units)])
        date_day = np.array(
            [date.strftime('%Y-%m-%d') for date in num2date(date, ds.TIME.units)])

        dates_uniques = np.unique(date_day)
        dates_ordered = {}
        dates_ordered["date_picker"] = [date_day[0], date_day[len(date_all) - 1]]

        list_obj_uniqdates = []
        for date_unique in dates_uniques:
            dict_date = {}
            indices_date = np.where(date_day == date_unique)
            dict_date[date_unique] = {
                "latitude": latitude[indices_date],
                "longitude": longitude[indices_date],
                "date_init": date_all[indices_date[0][0]],
                "date_fin": date_all[indices_date[0][len(indices_date[0]) - 1]]
            }
            list_obj_uniqdates.append(dict_date)

        coordinates["coordinates"] = list_obj_uniqdates

        variables_available = ["PSAL", "TEMP", "CNDC", "PRES", "CHLA", "TURBIDITY"]
        data_dataset["names"] = []
        for var in list(ds.variables):
            if var in variables_available:
                data_dataset["names"].append({
                    "standard_name": ds.variables[var].attrs['standard_name'].replace("_", " ").capitalize(),
                    "variable_name": var,
                    "url": url
                })
        data["data"] = data_dataset
        # data["data"] = dates_ordered
        USV_DATA.append(coordinates)
        USV_DATA.append(data)
        position = {}
        position["first_coordinate"] = [latitude[0], longitude[0]]
        position["last_coordinate"] = [latitude[len(latitude) - 1], longitude[len(longitude) - 1]]
        info_glider ={}
        USV_DATA.append(position)
        info_glider["date_start"] = ds.attrs['time_coverage_start']
        info_glider["date_end"] = ds.attrs['time_coverage_end']
        info_glider["url_download"] = url.replace("dodsC", "fileServer")
        info_glider["url"] = url
        info_glider["name"] = url.split('/')[-1]
        info_glider["summary"] = ds.attrs['summary']
        USV_DATA.append(info_glider)
        USV_DATA.append(dates_ordered)
        dataset["USV_DATA"] = USV_DATA
        return dataset

    def get_data_properties_from_glider(self, url, variable_name):
        ds = xr.open_dataset(url, decode_times=False)
        dict_complete = {}
        dict_complete["url"] = [url]
        date = ds.TIME.values
        variable = ds[variable_name].values
        latitude = ds.LATITUDE.values
        longitude = ds.LONGITUDE.values
        indices_deleted = np.where((np.isnan(variable)))
        indices_latitude = np.where((np.isnan(latitude)))
        dict_complete["index_deleted"] = indices_deleted[0].flatten()
        # indice_date = np.where(
        #     (~np.isnan(date)) & (~np.isnan(variable))
        # )
        indice_variables = np.where(
            (~np.isnan(variable))
        )

        # date = date[indice_date]
        date = date[indice_variables]
        variable = variable[indice_variables]
        latitude = latitude[indice_variables]
        longitude = longitude[indice_variables]

        date = np.array(
            [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(date, ds.TIME_GPS.units)])
        my_date = np.array(
            [date.strftime('%Y-%m') for date in num2date(ds.TIME.values, ds.TIME.units)])
        print("dateee: ", set(my_date))
        dict_select = {}
        dataset = {}
        try:
            units = ds.variables[variable_name].attrs['units'].replace("_", " ").capitalize()
        except:
            units = "Not units"

        for coords in list(ds[variable_name].coords):
            if coords == 'TIME':
                dict_select['type_chart'] = "basic"
                dict_select['value_coord'] = ""
                dataset['values'] = [[i, j] for i, j in
                                     zip(date.flatten(),
                                         np.around(np.float64(variable.flatten()), 3)) if
                                     not (pd.isnull(i) or pd.isnull(j))]
                dataset['coordinates'] = [[i, j] for i, j in zip(latitude,longitude) if
                                     not (pd.isnull(i) or pd.isnull(j))]
                dataset['units'] = units
                dataset['axis'] = [coords,
                                   ds.variables[variable_name].attrs['standard_name'].replace("_", " ").capitalize()]
                dataset['short_names'] = [coords, variable_name]
            else:
                dict_select['type_chart'] = "basic"
                dict_select['value_coord'] = ""
                dataset['values'] = [[]]
                dataset['units'] = "Not units"
                dataset['axis'] = []
                dataset['short_names'] = []
            dict_select["dataset"] = dataset
            dict_complete["variable_info"] = dict_select
            return dict_complete

    def get_data_properties_from_glider_two(self, url, variable_name, dateInit, dateFin):
        ds = xr.open_dataset(url, decode_times=False)
        dict_complete = {}
        dict_complete["url"] = [url]
        ts_init = ((datetime.strptime(dateInit, '%Y-%m-%d') - timedelta(days=1)) - datetime(1970, 1, 1)).total_seconds()
        ts_fin = ((datetime.strptime(dateFin, '%Y-%m-%d') + timedelta(days=1)) - datetime(1970, 1, 1)).total_seconds()
        tuple_index_range = np.where((ts_init <= ds.TIME.values) & (ds.TIME.values <= ts_fin))
        variable = ds[variable_name].values[tuple_index_range[0]]
        date = ds.TIME.values[tuple_index_range[0]]
        latitude = ds.LATITUDE.values[tuple_index_range[0]]
        longitude = ds.LONGITUDE.values[tuple_index_range[0]]

        indices_deleted = np.where((np.isnan(variable)))
        dict_complete["index_deleted"] = indices_deleted[0].flatten()
        indice_variables = np.where(
            (~np.isnan(variable))
        )

        date = date[indice_variables]
        variable = variable[indice_variables]
        latitude = latitude[indice_variables]
        longitude = longitude[indice_variables]

        dates_datetime = np.array(list(map(lambda x: np.datetime64(int(x), 's'), date)))
        date_utc = np.datetime_as_string(dates_datetime, unit='s')
        date = np.array(list(map(lambda s: s.replace('T', ' '), date_utc)))

        dict_select = {}
        dataset = {}
        try:
            units = ds.variables[variable_name].attrs['units'].replace("_", " ").capitalize()
        except:
            units = "Not units"

        for coords in list(ds[variable_name].coords):
            if coords == 'TIME':
                dataset['values'] = [[i, j] for i, j in
                                     zip(date.flatten(),
                                         np.around(np.float64(variable.flatten()), 3)) if
                                     not (pd.isnull(i) or pd.isnull(j))]
                dataset['coordinates'] = [[i, j] for i, j in zip(latitude,longitude) if
                                     not (pd.isnull(i) or pd.isnull(j))]
                dataset['units'] = units
                dataset['axis'] = [coords,
                                   ds.variables[variable_name].attrs['standard_name'].replace("_", " ").capitalize()]
                dataset['short_names'] = [coords, variable_name]
            else:
                dataset['values'] = [[]]
                dataset['units'] = "Not units"
                dataset['axis'] = []
                dataset['short_names'] = []
            dict_select["dataset"] = dataset
            dict_complete["variable_info"] = dict_select
            return dict_complete



