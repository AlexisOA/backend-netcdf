from siphon.catalog import *
import xarray as xr
import numpy as np
import netCDF4
from netCDF4 import num2date, date2num, date2index
import pandas as pd

class DataFiles:

    def get_profiles_shipbased(self, url, url_download):
        dict_complete = {}
        first_url = url[0]
        dict_complete["type"] = "basic"
        dict_complete["url"] = url
        dict_complete["url_download"] = url_download
        dict_arr = []
        ds_unique = xr.open_dataset(first_url, decode_times=False)


        vars = filter(lambda vars: 'QC' not in vars, list(ds_unique.data_vars))
        arr_standardnames = []
        for i in list(vars):
            try:
                standard_name = ds_unique.variables[i].attrs['standard_name'].replace("_"," ").capitalize()
            except:
                standard_name = ds_unique.variables[i].attrs['long_name'].replace("_"," ").capitalize()
            arr_standardnames.append(standard_name)
            # dict_select['name_data'] = standard_name
            # dict_select['Standard_name'] = standard_name
            # dict_select['Variable_name'] = standard_name


        for file_url in url:
            ds = xr.open_dataset(file_url, decode_times=False)
            my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
            for idx, variable_filter in enumerate(list(my_filtered)):
                dict_select = {}
                for coords in list(ds[variable_filter].coords):
                    # Si estamos ante una coordenada distinta de TIME
                    dataset = {}
                    if coords != 'TIME':
                        dict_select['Standard_name_coord'] = coords
                        # Si DEPTH es mayor que TIME, estamos ante un highchart de primera orden, DEPTH X TEMP en una única fecha
                        if len(ds[coords].values.flatten()) > len(ds['TIME'].values.flatten()):
                            dict_select['type_chart'] = "basic"
                            print("PRIMERA OPCION BASIC")
                            dataset['values'] = [[i, j] for i, j in
                                                 zip(np.around(np.float64(ds[variable_filter].values.flatten()),
                                                               3),
                                                     np.around(np.float64(ds[coords].values.flatten()), 3)) if
                                                 not (pd.isnull(i) or pd.isnull(j))]
                dict_select["dataset"] = dataset
                dict_arr.append(dict_select)


    def get_sediments_trap_data(self,  ds, dict_coord):
        dict_arr = []
        my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
        for variable in list(my_filtered):
            dict_select = {}
            dict_info = {}
            container_info = []
            try:
                name = ds.variables[variable].attrs['description'].replace("_", " ").capitalize()
            except:
                name = ds.variables[variable].attrs['standard_name'].replace("_", " ").capitalize()

            try:
                units = ds.variables[variable].attrs['units'].replace("_", " ").capitalize()
            except:
                units = "Not units"

            try:
                value_min = ds.variables[variable].attrs['valid_min']
            except:
                value_min = "Not value min"

            try:
                value_max = ds.variables[variable].attrs['valid_max']
            except:
                value_max = "Not value max"

            dict_select['name_data'] = str(variable).lower().capitalize()
            dict_select['Standard_name'] = name
            dict_info['Units'] = units
            dict_info['Min_value'] = value_min
            dict_info['Max_value'] = value_max
            container_info.append(dict_info)
            dict_select['info'] = container_info
            dataset = {}
            units = [dict_info['Units']]
            if "flux" in name:
                generate_data = True
                dict_select['show_data'] = True
            else:
                generate_data = False
                dict_select['show_data'] = False
                dataset['values'] = [[i, j] for i, j in
                                     zip(dict_coord["TIME"].flatten(),
                                         ds[variable].values.flatten()) if
                                     not (pd.isnull(i) or pd.isnull(j))]
            if generate_data:
                for coords in list(ds[variable].coords):
                    # Si las coordenadas de TEMP son > 1, estamos ante el caso que TEMP dependa de 2 coordenadas
                    if len(list(ds[variable].coords)) > 1:
                        # Si estamos ante una coordenada distinta de TIME
                        if coords != 'TIME':
                            dict_select['Standard_name_coord'] = coords
                            units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
                            # Si DEPTH es mayor que TIME, estamos ante un highchart de primera orden, DEPTH X TEMP en una única fecha
                            if len(dict_coord[coords]) > len(dict_coord['TIME']):
                                dict_select['type_chart'] = "basic"
                                print("PRIMERA OPCION BASIC")
                                dataset['values'] = [[i, j] for i, j in
                                                     zip(np.around(np.float64(ds[variable].values.flatten()),
                                                                   3),
                                                         np.around(np.float64(dict_coord[coords].flatten()), 3)) if
                                                     not (pd.isnull(i) or pd.isnull(j))]
                                dataset['units'] = units
                            else:
                                # Aqui entramos en múltiples fechas, pero DEPTH puede ser de solo un elemento o multidepth
                                if ds[coords].size > 1:
                                    dict_select['type_chart'] = "multiple"
                                    for i in range(len(ds[coords].values)):
                                        dataset['values'] = [[j, k] for j, k in
                                                             zip(dict_coord['TIME'].flatten(), np.around(
                                                                 np.float64(ds.variables[variable].values[:,
                                                                            int(i)].flatten()), 2)) if
                                                             not (pd.isnull(j) or pd.isnull(k))]
                                        dataset['units'] = units
                                        dataset['value_coord'] = np.around(np.float64(ds[coords].values[i]), 2)
                                        dataset = {}

                                else:
                                    dict_select['type_chart'] = "complex"
                                    dict_select['value_coord'] = dict_coord[coords].flatten()
                                    print("TERCERA OPCION COMPLEX--")
                                    # data = [[i, j] for i, j in zip(dict_complete['TIME'].flatten(), itertools.cycle(dict_complete[coords].flatten()))]
                                    dataset['values'] = [[i, j] for i, j in
                                                         zip(dict_coord['TIME'].flatten(),
                                                             np.around(
                                                                 np.float64(ds[variable].values.flatten()),
                                                                 2)) if
                                                         not (pd.isnull(i) or pd.isnull(j))]
                                    dataset['units'] = units
                    else:
                        units.append("")
                        if coords == 'TIME':
                            print("TERCERA OPCION COMPLEX 2--")
                            dict_select['type_chart'] = "complex"
                            dict_select['Standard_name_coord'] = variable
                            dict_select['value_coord'] = ""
                            dataset['values'] = [[i, j] for i, j in
                                                 zip(dict_coord[coords].flatten(),
                                                     np.around(np.float64(ds[variable].values.flatten()), 3)) if
                                                 not (pd.isnull(i) or pd.isnull(j))]
                            dataset['units'] = units
                        else:
                            dict_select['type_chart'] = "basic"
                            dict_select['value_coord'] = ""
                            dataset['values'] = [[i, j] for i, j in
                                                 zip(np.around(np.float64(ds[variable].values.flatten()), 2),
                                                     np.around(np.float64(dict_coord[coords].flatten()), 2)) if
                                                 not (pd.isnull(i) or pd.isnull(j))]
                            dataset['units'] = units
            dict_select["description"] = ds.attrs['summary'] + ", from " + ds.attrs['time_coverage_start'] + " to " + \
                                         ds.attrs['time_coverage_end'] + "."
            dict_select["dataset"] = dataset
            dict_arr.append(dict_select)
        return dict_arr

    def get_data_meteo(self, ds, dict_coord):
        dict_arr = []
        my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
        # return list(my_filtered)
        for variable in list(my_filtered):
            if "station_name" in variable:
                continue
            dict_select = {}
            dict_info = {}
            container_info = []

            try:
                name = ds.variables[variable].attrs['standard_name'].replace("_", " ").capitalize()
            except:
                name = "not description"

            try:
                units = ds.variables[variable].attrs['units'].replace("_", " ").capitalize()
            except:
                units = "Not units"

            try:
                value_min = ds.variables[variable].attrs['valid_min']
            except:
                value_min = "Not value min"

            try:
                value_max = ds.variables[variable].attrs['valid_max']
            except:
                value_max = "Not value max"

            dict_select['name_data'] = str(variable).lower().capitalize()
            dict_select['Standard_name'] = name
            dict_info['Units'] = units
            dict_info['Min_value'] = value_min
            dict_info['Max_value'] = value_max
            container_info.append(dict_info)
            dict_select['info'] = container_info
            dict_select['show_data'] = True
            dataset = {}
            units = [dict_info['Units']]
            print(variable)
            for coords in list(ds[variable].coords):
                if len(list(ds[variable].coords)) > 1:
                    if coords != 'TIME':
                        dict_select['Standard_name_coord'] = coords
                        units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
                        dict_select['type_chart'] = "meteo"
                        dict_select['value_coord'] = dict_coord[coords].flatten()
                        # dataset['values'] = [[i, j, k] for i, j, k in
                        #      zip(np.around(np.float64(ds[variable].values.flatten()), 2), dict_coord['TIME'],
                        #          itertools.cycle(np.float64(ds[coords].values).flatten())) if
                        #      not (pd.isnull(i) or pd.isnull(j) or pd.isnull(k))]
                        dataset['values'] = [[i, j] for i, j in
                                             zip(dict_coord['TIME'], np.around(np.float64(ds[variable].values.flatten()), 2)) if
                                             not (pd.isnull(i) or pd.isnull(j))]
                        # dataset['values'] = np.around(np.float64(ds[variable].values.flatten()), 2)
                        dataset['units'] = units
                else:
                    dict_select['Standard_name_coord'] = variable
                    units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
                    dict_select['type_chart'] = "meteo"
                    dict_select['value_coord'] = ""
                    dataset['values'] = [[i, j] for i, j in
                                         zip(dict_coord['TIME'],
                                             np.around(np.float64(ds[variable].values.flatten()), 2)) if
                                         not (pd.isnull(i) or pd.isnull(j))]
                    # dataset['values'] = np.around(np.float64(ds[variable].values.flatten()), 2)
                    dataset['units'] = units
            dict_select["description"] = ds.attrs['summary'] + ", from " + ds.attrs[
                'time_coverage_start'] + " to " + \
                                         ds.attrs['time_coverage_end'] + "."
            dict_select["dataset"] = dataset
            dict_arr.append(dict_select)
        return dict_arr


    def get_data_select_antiguo(self, url, url_download):
        ds = xr.open_dataset(url, decode_times=False)
        # if ds.attrs['keywords'] == 'sediments': return self.get_sediments_trap_data(ds, url, url_download)
        try:
            keywrds = ds.attrs['keywords']
        except:
            keywrds = ""

        dict_complete = {}
        dict_complete["name"] = url.split('/')[-1]
        dict_complete["type"] = "basic"
        dict_complete["url"] = url
        dict_complete["url_download"] = url_download
        dict_complete['date_from'] = ds.attrs['time_coverage_start']
        dict_complete['date_to'] = ds.attrs['time_coverage_end']

        dict_coord = {}
        for coord in list(ds.coords):
            if coord == 'TIME':
                my_date = np.array(
                    [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(ds.TIME.values, ds.TIME.units)])
                dict_coord[coord] = my_date
                continue
            dict_coord[coord] = ds[coord].values

        if "Meteo" in url or "wind" in keywrds.lower() or "dm_meteo" in url:
            arr_dict = self.get_data_meteo(ds, dict_coord)
            dict_complete["table_info"] = arr_dict
            return dict_complete
        if "sediments" in keywrds.lower() or "sediments" in url.lower():
            arr_dict = self.get_sediments_trap_data(ds, dict_coord)
            dict_complete["table_info"] = arr_dict
            return dict_complete
        dict_arr = []
        colors = []
        my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
        for varirable_filter in list(my_filtered):
            dict_select = {}
            dict_info = {}
            container_info = []

            try:
                standard_name = ds.variables[varirable_filter].attrs['standard_name'].replace("_"," ").capitalize()
            except:
                standard_name = ds.variables[varirable_filter].attrs['long_name'].replace("_"," ").capitalize()
            try:
                variable_name = ds.variables[varirable_filter].attrs['variable_name'].replace("_"," ").capitalize()
            except:
                variable_name = ds.variables[varirable_filter].attrs['long_name'].replace("_"," ").capitalize()

            try:
                units = ds.variables[varirable_filter].attrs['units'].replace("_", " ").capitalize()
            except:
                units = "Not units"

            try:
                value_min = ds.variables[varirable_filter].attrs['valid_min']
            except:
                value_min = "Not value min"

            try:
                value_max = ds.variables[varirable_filter].attrs['valid_max']
            except:
                value_max = "Not value max"

            dict_select['name_data'] = str(varirable_filter).lower().capitalize()
            dict_select['Standard_name'] = standard_name
            dict_select['Variable_name'] = variable_name
            dict_info['Units'] = units
            dict_info['Min_value'] = value_min
            dict_info['Max_value'] = value_max
            container_info.append(dict_info)
            dict_select['info'] = container_info
            dataset = {}
            dataset_multiple = []
            units = [dict_info['Units']]
            dict_select['show_data'] = True
            for coords in list(ds[varirable_filter].coords):
                # Si las coordenadas de TEMP son > 1, estamos ante el caso que TEMP dependa de 2 coordenadas
                if len(list(ds[varirable_filter].coords)) > 1:
                    # Si estamos ante una coordenada distinta de TIME
                    if coords != 'TIME':
                        dict_select['Standard_name_coord'] = coords
                        units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
                        # Si DEPTH es mayor que TIME, estamos ante un highchart de primera orden, DEPTH X TEMP en una única fecha
                        if len(dict_coord[coords]) > len(dict_coord['TIME']):
                            dict_select['type_chart'] = "basic"
                            print("PRIMERA OPCION BASIC")
                            dataset['values'] = [[i, j] for i, j in
                                                 zip(np.around(np.float64(ds[varirable_filter].values.flatten()),
                                                               3),
                                                     np.around(np.float64(dict_coord[coords].flatten()), 3)) if
                                                 not (pd.isnull(i) or pd.isnull(j))]
                            dataset['units'] = units
                        else:
                            # Aqui entramos en múltiples fechas, pero DEPTH puede ser de solo un elemento o multidepth
                            if ds[coords].size > 1:
                                if len(colors) == 0:
                                    import random
                                    for i in range(len(ds[coords].values)):
                                        random_number = random.randint(0, 16777215)
                                        hex_number = str(hex(random_number))
                                        hex_number = '#' + hex_number[2:]
                                        colors.append(hex_number)
                                dict_select['type_chart'] = "multiple"
                                for i in range(len(ds[coords].values)):
                                    dataset['values'] = [[j, k] for j, k in
                                                         zip(dict_coord['TIME'].flatten(), np.around(
                                                             np.float64(ds.variables[varirable_filter].values[:,
                                                                        int(i)].flatten()), 2)) if
                                                         not (pd.isnull(j) or pd.isnull(k))]
                                    dataset['units'] = units
                                    dataset['value_coord'] = np.around(np.float64(ds[coords].values[i]),2)
                                    dataset_multiple.append(dataset)
                                    dataset = {}

                            else:
                                dict_select['type_chart'] = "complex"
                                dict_select['value_coord'] = dict_coord[coords].flatten()
                                print("TERCERA OPCION COMPLEX--")
                                # data = [[i, j] for i, j in zip(dict_complete['TIME'].flatten(), itertools.cycle(dict_complete[coords].flatten()))]
                                dataset['values'] = [[i, j] for i, j in
                                                     zip(dict_coord['TIME'].flatten(),
                                                         np.around(
                                                             np.float64(ds[varirable_filter].values.flatten()),
                                                             2)) if
                                                     not (pd.isnull(i) or pd.isnull(j))]
                                dataset['units'] = units
                else:
                    units.append("")
                    if coords == 'TIME':
                        print("TERCERA OPCION COMPLEX 2--")
                        dict_select['type_chart'] = "complex"
                        dict_select['Standard_name_coord'] = varirable_filter
                        dict_select['value_coord'] = ""
                        dataset['values'] = [[i, j] for i, j in
                                             zip(dict_coord[coords].flatten(),
                                                 np.around(np.float64(ds[varirable_filter].values.flatten()), 3)) if
                                             not (pd.isnull(i) or pd.isnull(j))]
                        dataset['units'] = units
                    else:
                        dict_select['type_chart'] = "basic"
                        dict_select['value_coord'] = ""
                        dataset['values'] = [[i, j] for i, j in
                                             zip(np.around(np.float64(ds[varirable_filter].values.flatten()), 2),
                                                 np.around(np.float64(dict_coord[coords].flatten()), 2)) if
                                             not (pd.isnull(i) or pd.isnull(j))]
                        dataset['units'] = units
            dict_select["description"] = ds.attrs['summary'] + ", from " + ds.attrs['time_coverage_start'] + " to " + \
                                         ds.attrs['time_coverage_end'] + "."
            dict_select["dataset"] = dataset
            dict_select["dataset_multiple"] = dataset_multiple
            dict_select["colors"] = colors
            dict_arr.append(dict_select)
        dict_complete["table_info"] = dict_arr
        return dict_complete