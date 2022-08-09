import requests
from siphon.catalog import *
import xarray as xr
import numpy as np

class ThreddsCatalog:

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
        print(ds.dims)
        print("-----------")
        print(ds.attrs)
        print("-----------")
        print(ds.coords)
        print("--------")
        print(ds.data_vars)
        print("-------****")
        print(ds.PSAL.values)
        print("-------@@@")
        depth = ds.DEPTH.values
        depth_masked = np.where(depth[:] != None)
        print(np.asarray(depth_masked))
        print(len(np.asarray(depth_masked)[0]))
        print(depth)
        print(depth[3672])
        print(len(depth))
        print("__________________________________")
        depth_mascara = (depth[:])
        dict = {}
        dict['coords'] = [ds.LATITUDE.values[0], ds.LONGITUDE.values[0]]
        # dict['Longitude'] = ds.LONGITUDE.values
        return dict
