import requests
from siphon.catalog import *
import xarray as xr
import numpy as np
import json
import matplotlib.pyplot as plt
import sys
import numpy as np
import io
import base64


class ThreddsCatalog:

    def __init__(self):
        print("Constructor Function")

    def get_layers_test(self):
        with open('C:/Users/Plocan8/Documents/sample.json') as d:
            dictData = json.load(d)
            return dictData

    def get_graphic_from_nc_file(self):
        fn = "C:/Users/Plocan8/Documents/files_netcdf/OS_ESTOC_201902_D_CTD-P4.nc"
        ds = xr.open_dataset(fn, decode_times=False)
        # print(ds.variables)
        times = ds.TIME
        depths = ds.DEPTH
        temperatures = ds.TEMP
        psal = ds.PSAL
        cphl = ds.CPHL
        doxy = ds.DOXY
        figure, axis = plt.subplots(2, 2)
        for idx, time in enumerate(times.values):
            axis[0, 0].plot(temperatures.values[idx], depths.values, color="red")
            axis[0, 0].set_title("Temperature", fontsize=10)
            axis[0, 0].set(xlabel='Temperature', ylabel='Depth')
            axis[0, 0].invert_yaxis()

            axis[0, 1].plot(psal.values[idx], depths.values, color="purple")
            axis[0, 1].set_title("Practical Salinity (PSU)", fontsize=10)
            axis[0, 1].set(xlabel='Salinity', ylabel='Depth')
            axis[0, 1].invert_yaxis()

            axis[1, 0].plot(cphl.values[idx], depths.values, color="green")
            axis[1, 0].set_title("Chloropyll", fontsize=10)
            axis[1, 0].set(xlabel='Chloropyll', ylabel='Depth')
            axis[1, 0].invert_yaxis()

            axis[1, 1].plot(doxy.values[idx], depths.values, color="blue")
            axis[1, 1].set_title("Oxigen in water", fontsize=10)
            axis[1, 1].set(xlabel='Oxigen', ylabel='Depth')
            axis[1, 1].invert_yaxis()

            figure.tight_layout()
            f = io.BytesIO()
            plt.savefig(f, format="png", dpi=72)
            f.seek(0)
            encoded_img = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
            json_data = {}
            json_data['base64Data'] = encoded_img
            f.close()
            return json_data

    def get_first_layer_from_thredds(self, url):
        top_catalog = TDSCatalog(url)
        res = []
        if len(top_catalog.catalog_refs) > 0:
            for ref_ in top_catalog.catalog_refs:
                dict = {}
                ref = top_catalog.catalog_refs[ref_]
                dict['id'] = ref_
                dict['name'] = ref_
                dict['url'] = ref.href
                dict['children'] = []
                res.append(dict)
        else:
            for idx, data in enumerate(top_catalog.datasets.values()):
                dict = {}
                dict['id'] = str(data)
                dict['name'] = str(data)
                dict['url'] = data.access_urls['OPENDAP']
                dict['children'] = []
                res.append(dict)
                # ds = xr.open_dataset(data.access_urls['OPENDAP'], decode_times=False)
                # print(ds.LATITUDE.values)
                # print(type(ds.LATITUDE.values))
        return res

    def get_marker_coords_from_thredds(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        dict = {}
        dict['id'] = url
        dict['coords'] = [ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]
        # getting time, depth and temperature
        times = ds.TIME
        depths = ds.DEPTH
        temperatures = ds.TEMP
        children = []
        for idx, time in enumerate(times.values):
            dataset = []
            obj = {}
            obj['time'] = time
            for temp, depth in zip(temperatures.values[idx], depths.values):
                data_obj = {}
                data_obj["temperature"] = round(temp.item(), 2)
                data_obj["depth"] = round(depth.item(), 2)
                dataset.append(data_obj)
            obj['data'] = dataset
            children.append(obj)

        dict['children'] = children
        # dict['Longitude'] = ds.LONGITUDE.values
        return dict

    def get_coords_local_files(self, name):
        fn = "C:/Users/Plocan8/Documents/files_netcdf/" + str(name) + ".nc"
        ds = xr.open_dataset(fn, decode_times=False)
        dict = {}
        dict['id'] = name
        dict['coords'] = [[ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]]
        ds.close()
        return dict


    def get_graphic_from_local_file(self, name):
        print(name)
        fn = "C:/Users/Plocan8/Documents/files_netcdf/" + str(name) + ".nc"
        ds = xr.open_dataset(fn, decode_times=False)
        # print(ds.variables)
        times = ds.TIME
        depths = ds.DEPTH
        temperatures = ds.TEMP
        psal = ds.PSAL
        cphl = ds.CPHL
        doxy = ds.DOXY
        figure, axis = plt.subplots(2, 2)
        for idx, time in enumerate(times.values):
            axis[0, 0].plot(temperatures.values[idx], depths.values, color="red")
            axis[0, 0].set_title("Temperature", fontsize=10)
            axis[0, 0].set(xlabel='Temperature', ylabel='Depth')
            axis[0, 0].invert_yaxis()

            axis[0, 1].plot(psal.values[idx], depths.values, color="purple")
            axis[0, 1].set_title("Practical Salinity (PSU)", fontsize=10)
            axis[0, 1].set(xlabel='Salinity', ylabel='Depth')
            axis[0, 1].invert_yaxis()

            axis[1, 0].plot(cphl.values[idx], depths.values, color="green")
            axis[1, 0].set_title("Chloropyll", fontsize=10)
            axis[1, 0].set(xlabel='Chloropyll', ylabel='Depth')
            axis[1, 0].invert_yaxis()

            axis[1, 1].plot(doxy.values[idx], depths.values, color="blue")
            axis[1, 1].set_title("Oxigen in water", fontsize=10)
            axis[1, 1].set(xlabel='Oxigen', ylabel='Depth')
            axis[1, 1].invert_yaxis()

            figure.tight_layout()
            f = io.BytesIO()
            plt.savefig(f, format="png", dpi=72)
            f.seek(0)
            encoded_img = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
            json_data = {}
            json_data['base64Data'] = encoded_img
            f.close()
            ds.close()
            return json_data
