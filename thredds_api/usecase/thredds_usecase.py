from siphon.catalog import *
import xarray as xr
import json
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import netCDF4
from netCDF4 import num2date, date2num, date2index
import pandas as pd
import math

class ThreddsCatalog:

    def get_layers_test(self):
        with open('C:/Users/Plocan8/Documents/sample.json') as d:
            dictData = json.load(d)
            return dictData

    def get_marker_coords_from_thredds(self, url):
        # print("Marcadores del thredds: ", url)
        ds = xr.open_dataset(url, decode_times=False)
        dict = {}
        name = url.split('/')
        # print("datavars: ", ds.data_vars)
        # print("coords: ", type(ds.coords))
        dict['name'] = name[-1]
        dict['id'] = url
        dict['coords'] = [[ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]]
        # print(ds.LATITUDE.values[0], ds.LONGITUDE.values[0])
        return dict

    def get_marker_array_coords_from_thredds(self, url):
        store_dict = []
        for url_data in url:
            # print(url_data)
            ds = xr.open_dataset(url_data, decode_times=False)
            name = url_data.split('/')
            dict = {}
            # print("datavars: ", ds.data_vars)
            # print("coords from: ", name, " --> ", [ds.LATITUDE.values[0], ds.LONGITUDE.values[0]])
            dict['name'] = name[-1]
            dict['id'] = url_data
            dict['coords'] = [ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]
            store_dict.append(dict)
        return store_dict

    def get_data_from_file_to_map(self, url):
        print("Marcadores del thredds: ", url)
        f = netCDF4.Dataset(url)
        dict_site = {}
        dict_site['url'] = url
        dict_site['Name'] = f.getncattr('id')
        dict_site['Description'] = f.getncattr('summary')
        dict_site['Area'] = f.getncattr('area')
        dict_site['Latitude'] = f.getncattr('geospatial_lat_min')
        dict_site['Longitude'] = f.getncattr('geospatial_lon_max')
        dict_site['Datefrom'] = f.getncattr('time_coverage_start')
        dict_site['Dateto'] = f.getncattr('time_coverage_end')
        if 'DEPTH' in list(f.variables.keys()):
            dict_site['Depth'] = -(int(f.variables['DEPTH'].valid_min))

        dict_properties = {}
        # print(f.variables.keys())
        filtered = filter(lambda vars: 'QC' not in vars, list(f.variables.keys()))
        # dict_properties['Properties'] = list(filtered)
        properties_long_name = []
        for var in list(filtered):
            var_info = f.variables[var]
            properties_long_name.append("%s %s %s %s" % (var_info.long_name, '(', var, ')'))
        dict_properties['Properties'] = properties_long_name

        dict_file = {}
        dict_file['site'] = dict_site
        dict_file['properties_file'] = dict_properties

        return dict_file

    def get_coords_local_files(self, name):
        fn = "C:/Users/Plocan8/Documents/files_netcdf/" + str(name) + ".nc"
        ds = xr.open_dataset(fn, decode_times=False)
        dict = {}
        dict['id'] = name
        dict['coords'] = [[ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]]
        ds.close()
        return dict

    def get_data_plot_forms(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        name = url.split('/')
        coords = list(ds.coords)
        json_data = {}
        json_data['name'] = name[-1]
        json_data['url'] = url
        json_data['dimensions'] = coords
        json_data["coords"] = []
        for coord in coords:
            if coord == 'TIME':
                dates = num2date(ds[coord].values, ds[coord].units)
                date_arr = [date.strftime('%Y-%m') for date in dates]
                coord_dim = {coord: set(date_arr)}
                json_data["coords"].append(coord_dim)
                continue
            # if coord != 'LATITUDE' and coord != 'LONGITUDE':
            #     coord_dim = {"PARAM": coord}
            #     json_data["coords"].append(coord_dim)
            #     continue
            data = np.around(np.float64(ds[coord].values), 3)
            coord_dim = {coord: data.flatten()}
            json_data["coords"].append(coord_dim)
        print(json_data)
        return [json_data]

    def get_data_select(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        dict_complete = {}
        dict_complete["name"] = url.split('/')[-1]
        dict_complete["type"] = "basic"
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

        dict_arr = []
        my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
        for varirable_filter in list(my_filtered):
            dict_select = {}
            dict_info = {}
            container_info = []
            dict_select['Standard_name'] = ds.variables[varirable_filter].attrs['standard_name'].replace("_",
                                                                                                         " ").capitalize()
            try:
                dict_select['Variable_name'] = ds.variables[varirable_filter].attrs['variable_name'].replace("_",
                                                                                                             " ").capitalize()
            except:
                dict_select['Variable_name'] = ds.variables[varirable_filter].attrs['long_name'].replace("_",
                                                                                                         " ").capitalize()
            dict_select['name_data'] = varirable_filter
            dict_info['Units'] = ds.variables[varirable_filter].attrs['units'].replace("_", " ").capitalize()
            dict_info['Min_value'] = ds.variables[varirable_filter].attrs['valid_min']
            dict_info['Max_value'] = ds.variables[varirable_filter].attrs['valid_max']
            container_info.append(dict_info)
            dict_select['info'] = container_info
            dataset = {}
            units = [dict_info['Units']]
            for coords in list(ds[varirable_filter].coords):
                if coords != 'TIME':
                    dict_select['Standard_name_coord'] = coords
                    units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
                    if len(dict_coord[coords]) > len(dict_coord['TIME']):
                        print("PRIMERA OPCION")
                        dataset['values'] = [[i, j] for i, j in
                                   zip( np.around(np.float64(ds[varirable_filter].values.flatten()), 2), np.around(np.float64(dict_coord[coords].flatten()), 2)) if not (pd.isnull(i) or pd.isnull(j))]
                    else:
                        if "multipledepth" in url.lower():
                            dict_complete["type"] = "multiple"
                            print("SEGUNDA OPCION")
                            print("Hay multidepth")
                        else:
                            dict_complete["type"] = "complex"
                            dict_select['value_coord'] = dict_coord[coords].flatten()
                            print("TERCERA OPCION")
                            # data = [[i, j] for i, j in zip(dict_complete['TIME'].flatten(), itertools.cycle(dict_complete[coords].flatten()))]
                            dataset['values'] = [[i, j] for i, j in
                                    zip(dict_coord['TIME'].flatten(), np.around(np.float64(ds[varirable_filter].values.flatten()), 3)) if not (pd.isnull(i) or pd.isnull(j))]
            dataset['units'] = units
            dict_select["description"] = ds.attrs['summary'] + ", from " + ds.attrs['time_coverage_start'] + " to " + \
                                           ds.attrs['time_coverage_end'] + "."
            dict_select["dataset"] = dataset
            dict_arr.append(dict_select)
        dict_complete["table_info"] = dict_arr
        return dict_complete

    # def get_data_select_antiguo(self, url):
    #     ds = xr.open_dataset(url, decode_times=False)
    #     dict_complete = {}
    #     dict_complete["name"] = url.split('/')[-1]
    #     dict_complete["type"] = "basic"
    #     dict_complete['date_from'] = ds.attrs['time_coverage_start']
    #     dict_complete['date_to'] = ds.attrs['time_coverage_end']
    #
    #     dict_coord = {}
    #     for coord in list(ds.coords):
    #         if coord == 'TIME':
    #             my_date = np.array(
    #                 [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(ds.TIME.values, ds.TIME.units)])
    #             dict_coord[coord] = my_date
    #             continue
    #         dict_coord[coord] = ds[coord].values
    #
    #     dict_arr = []
    #     my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
    #     for varirable_filter in list(my_filtered):
    #         dict_select = {}
    #         dict_info = {}
    #         container_info = []
    #         dict_select['Standard_name'] = ds.variables[varirable_filter].attrs['standard_name'].replace("_",
    #                                                                                                      " ").capitalize()
    #         try:
    #             dict_select['Variable_name'] = ds.variables[varirable_filter].attrs['variable_name'].replace("_",
    #                                                                                                          " ").capitalize()
    #         except:
    #             dict_select['Variable_name'] = ds.variables[varirable_filter].attrs['long_name'].replace("_",
    #                                                                                                      " ").capitalize()
    #         dict_select['name_data'] = varirable_filter
    #         dict_info['Units'] = ds.variables[varirable_filter].attrs['units'].replace("_", " ").capitalize()
    #         dict_info['Min_value'] = ds.variables[varirable_filter].attrs['valid_min']
    #         dict_info['Max_value'] = ds.variables[varirable_filter].attrs['valid_max']
    #         container_info.append(dict_info)
    #         dict_select['info'] = container_info
    #         dataset = {}
    #         units = [dict_info['Units']]
    #         for coords in list(ds[varirable_filter].coords):
    #             if len(list(ds[varirable_filter].coords)) > 1:
    #                 if coords != 'TIME':
    #                     dict_select['Standard_name_coord'] = coords
    #                     units.append(ds.variables[coords].attrs['units'].replace("_", " ").capitalize())
    #                     if len(dict_coord[coords]) > len(dict_coord['TIME']):
    #                         print("PRIMERA OPCION")
    #                         dataset['values'] = [[i, j] for i, j in
    #                                              zip(np.around(np.float64(ds[varirable_filter].values.flatten()), 2),
    #                                                  np.around(np.float64(dict_coord[coords].flatten()), 2)) if
    #                                              not (pd.isnull(i) or pd.isnull(j))]
    #                     else:
    #                         if ds[coords].size > 1:
    #                             dict_complete["type"] = "multiple"
    #                             print("SEGUNDA OPCION")
    #                             print("Hay multidepth")
    #                         else:
    #                             dict_complete["type"] = "complex"
    #                             dict_select['value_coord'] = dict_coord[coords].flatten()
    #                             print("TERCERA OPCION")
    #                             # data = [[i, j] for i, j in zip(dict_complete['TIME'].flatten(), itertools.cycle(dict_complete[coords].flatten()))]
    #                             dataset['values'] = [[i, j] for i, j in
    #                                                  zip(dict_coord['TIME'].flatten(),
    #                                                      np.around(np.float64(ds[varirable_filter].values.flatten()),
    #                                                                3)) if not (pd.isnull(i) or pd.isnull(j))]
    #             else:
    #                 dict_select['Standard_name_coord'] = ""
    #                 if coords == 'TIME':
    #                     dict_complete["type"] = "complex"
    #                     dict_select['value_coord'] = ""
    #                     dataset['values'] = [[i, j] for i, j in
    #                                          zip(dict_coord[coords].flatten(),
    #                                              np.around(np.float64(ds[varirable_filter].values.flatten()), 3)) if
    #                                          not (pd.isnull(i) or pd.isnull(j))]
    #         dataset['units'] = units
    #         dict_select["description"] = ds.attrs['summary'] + ", from " + ds.attrs['time_coverage_start'] + " to " + \
    #                                      ds.attrs['time_coverage_end'] + "."
    #         dict_select["dataset"] = dataset
    #         dict_arr.append(dict_select)
    #     dict_complete["table_info"] = dict_arr
    #     return dict_complete

    def  get_graphic_from_dataForm(self, obj):
        print(obj["url"])
        # ds = xr.open_dataset(obj.url, decode_times=False)
        data_alls = [k for k, v in obj.items() if v == 'All']
        print("One line Code Key value: ", [k for k,v in obj.items() if v == 'All'])
        for all in data_alls:
            print(all)

        return ["hola"]





    def get_graphic_from_local_file(self, url):
        # fn = "C:/Users/Plocan8/Documents/files_netcdf/" + str(url) + ".nc"
        # ds = xr.open_dataset(fn, decode_times=False)
        ds = xr.open_dataset(url, decode_times=False)
        collection_image = []
        # print(ds.variables)
        name = url.split('/')
        # print(ds)
        times = ds.TIME
        # print("time: ",times.values)
        depths = ds.DEPTH
        # print("depth: ",depths.values)
        temperatures = ds.TEMP
        # print("temp: ",temperatures.values)
        # print("temp flatter: ", temperatures.values.flatten())
        psal = ds.PSAL
        # print("psal: ",psal.values)
        cphl = ds.CPHL
        # print("cphl: ",cphl.values)
        doxy = ds.DOXY
        # print("doy: ", doxy.values)
        figure, axis = plt.subplots(2, 2)

        for idx, time in enumerate(times.values):
            json_data = {}
            axis[0, 0].plot(temperatures.values.flatten(), depths.values, color="red")
            axis[0, 0].set_title("Temperature", fontsize=10)
            axis[0, 0].set(xlabel='Temperature', ylabel='Depth')
            axis[0, 0].invert_yaxis()

            axis[0, 1].plot(psal.values.flatten(), depths.values, color="purple")
            axis[0, 1].set_title("Practical Salinity (PSU)", fontsize=10)
            axis[0, 1].set(xlabel='Salinity', ylabel='Depth')
            axis[0, 1].invert_yaxis()

            axis[1, 0].plot(cphl.values.flatten(), depths.values, color="green")
            axis[1, 0].set_title("Chloropyll", fontsize=10)
            axis[1, 0].set(xlabel='Chloropyll', ylabel='Depth')
            axis[1, 0].invert_yaxis()

            axis[1, 1].plot(doxy.values.flatten(), depths.values, color="blue")
            axis[1, 1].set_title("Oxigen in water", fontsize=10)
            axis[1, 1].set(xlabel='Oxigen', ylabel='Depth')
            axis[1, 1].invert_yaxis()

            dates = num2date(times.values, times.units)
            date_arr = [date.strftime('%Y-%m-%d %H:%M:%S') for date in dates]
            datetime_id = "datetime_" + str(idx)
            json_data[datetime_id] = date_arr
            tittle = '%s - %s' % (name[-1], date_arr[0])
            figure.suptitle(tittle, fontsize='x-large')

            figure.tight_layout()
            f = io.BytesIO()
            plt.savefig(f, format="png", dpi=72)
            f.seek(0)
            encoded_img = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
            image_id = "base64Data_" + str(idx)
            json_data['id'] = str(idx)
            json_data['name'] = name[-1]
            json_data[image_id] = encoded_img
            json_data['coords'] = [ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]
            collection_image.append(json_data)

            f.close()
            ds.close()
            return collection_image

    def get_first_layer_from_thredds(self, url):
        top_catalog = TDSCatalog(url)
        res = []
        if len(top_catalog.catalog_refs) > 0:
            for ref_ in top_catalog.catalog_refs:
                dict = {}
                ref = top_catalog.catalog_refs[ref_]
                if(ref_ == "Test" or ref_ == "Gliders"): continue
                dict['id'] = ref_
                dict['name'] = ref_
                dict['url'] = ref.href
                dict['is_file'] = False
                dict['children'] = []
                res.append(dict)
            if len(top_catalog.datasets) > 0:
                gen_dict = self.aux_get_first_layer(top_catalog)
                for i in gen_dict:
                    res.append(i)
        else:
            gen_dict = self.aux_get_first_layer(top_catalog)
            for i in gen_dict:
                res.append(i)
        return res

    def aux_get_first_layer(self, catalog):
        for idx, data in enumerate(catalog.datasets.values()):
            dict = {}
            dict['id'] = str(data)
            dict['name'] = str(data)
            dict['url'] = data.access_urls['OPENDAP']
            dict['is_file'] = True
            dict['children'] = []
            # res.append(dict)
            # ds = xr.open_dataset(data.access_urls['OPENDAP'], decode_times=False)
            # print(ds.LATITUDE.values)
            # print(type(ds.LATITUDE.values))
            yield dict

