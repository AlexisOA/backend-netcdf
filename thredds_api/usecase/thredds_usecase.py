from siphon.catalog import *
import xarray as xr
import numpy as np
import netCDF4
from netCDF4 import num2date, date2num, date2index
import pandas as pd

class ThreddsCatalog:
    def get_info_file_for_popup_profiles(self, url_arrays, urlDownload_arrays):
        pass
    #Se está usando
    def get_info_file_for_popup(self, url, url_download):
        f = netCDF4.Dataset(url)
        dict_site = {}
        dict_site['url'] = url
        dict_site['url_download'] = url_download
        dict_site['Name'] = f.getncattr('id')
        dict_site['Description'] = f.getncattr('summary')
        dict_site['Area'] = f.getncattr('area')
        dict_site['Latitude'] = f.getncattr('geospatial_lat_min')
        dict_site['Longitude'] = f.getncattr('geospatial_lon_max')
        dict_site['Datefrom'] = f.getncattr('time_coverage_start')
        dict_site['Dateto'] = f.getncattr('time_coverage_end')
        # Este valor de DEPTH no es válido, quitarlo.
        if 'DEPTH' in list(f.variables.keys()):
            try:
                    dict_site['Depth'] = -(int(f.variables['DEPTH'].valid_min))
            except:
                dict_site['Depth'] = -1

        try:
            if "sediments" in f.getncattr('keywords'):
                properties = self.get_properties_from_sediments_trap(f)
                dict_file_sediment = {}
                dict_file_sediment['site'] = dict_site
                dict_file_sediment['properties_file'] = properties
                return dict_file_sediment
        except:
            pass
        dict_properties = {}
        # print(f.variables.keys())
        filtered = filter(lambda vars: 'QC' not in vars, list(f.variables.keys()))
        # dict_properties['Properties'] = list(filtered)
        properties_long_name = []
        for var in list(filtered):
            var_info = f.variables[var]
            try:
                properties_long_name.append("%s %s %s %s" % (var_info.long_name, '(', var, ')'))
                dict_properties['Properties'] = properties_long_name
            except:
                continue
        dict_file = {}
        dict_file['site'] = dict_site
        dict_file['properties_file'] = dict_properties

        return dict_file

    def get_properties_from_sediments_trap(self, f):
        dict_properties = {}
        properties_long_name = []
        for var in list(f.variables.keys()):
            if "flux" in f[var].long_name:
                print("SEDIMENTOOOOS")
                var_info = f.variables[var]
                try:
                    properties_long_name.append("%s %s %s %s" % (var_info.long_name, '(', var, ')'))
                    dict_properties['Properties'] = properties_long_name
                except:
                    continue
        return dict_properties
    # Se está usando
    def get_file_as_dataframe(self, url):
        ds = xr.open_dataset(url, decode_times=False)
        return ds.to_dataframe().reset_index()

    # Se está usando
    def get_fixedobs_layers_from_thredds(self, url):
        print(url)
        top_catalog = TDSCatalog(url)
        res = []
        if len(top_catalog.catalog_refs) > 0:
            for ref_ in top_catalog.catalog_refs:
                dict = {}
                ref = top_catalog.catalog_refs[ref_]
                if (ref_ == "Test" or ref_ == "Gliders" or ref_ == "UnderRevision"): continue
                dict['id'] = ref_
                dict['name'] = ref_
                dict['url'] = ref.href
                dict['is_file'] = False
                dict['is_profile'] = False
                dict['children'] = []
                res.append(dict)
            if len(top_catalog.datasets) > 0:
                if "ship-based" in url:
                    gen_dict = self.generate_layers_for_shipbased(top_catalog)
                    for i in gen_dict:
                        res.append(i)
                else:
                    gen_dict = self.aux_get_fixedobs_layers(top_catalog)
                    for i in gen_dict:
                        res.append(i)
        else:
            if "ship-based" in url: print("generating shipbased")
            gen_dict = self.aux_get_fixedobs_layers(top_catalog)
            for i in gen_dict:
                res.append(i)
        return res

    def generate_layers_for_shipbased(self, catalog):
        print("hola")
        groups_opendap = {}
        groups_http = {}
        for data in catalog.datasets.values():
            n = str(data).split('_')[2]
            if n in groups_opendap:
                groups_opendap[n].append(data.access_urls['OPENDAP'])
                groups_http[n].append(data.access_urls['HTTPServer'])
            else:
                groups_opendap[n] = [data.access_urls['OPENDAP']]
                groups_http[n] = [data.access_urls['HTTPServer']]

        for key, value in groups_opendap.items():
            dict_group = {}
            url_opendap = value[0]
            name_id = url_opendap[url_opendap.rindex('/') + 1:url_opendap.rindex('CTD')+3]
            dict_group['id'] = name_id
            dict_group['name'] = name_id
            dict_group['is_file'] = True
            dict_group['is_profile'] = True
            dict_group['children'] = []
            dict_group['url'] = value
            dict_group['url_download'] = groups_http[key]
            yield dict_group
    # Se está usando
    def aux_get_fixedobs_layers(self, catalog):
        for idx, data in enumerate(catalog.datasets.values()):
            dict = {}
            dict['id'] = str(data)
            dict['name'] = str(data)
            dict['url'] = data.access_urls['OPENDAP']
            dict['url_download'] = data.access_urls['HTTPServer']
            dict['is_file'] = True
            dict['is_profile'] = False
            dict['children'] = []
            yield dict

    def get_gliders_layers(self, url):
        top_catalog = TDSCatalog(url)
        res = []
        if len(top_catalog.catalog_refs) > 0:
            for ref_ in top_catalog.catalog_refs:
                dict = {}
                ref = top_catalog.catalog_refs[ref_]
                if ref_ != "Gliders" and "glider" not in url: continue

                dict['id'] = ref_
                dict['name'] = ref_
                dict['url'] = ref.href
                dict['is_file'] = False
                dict['is_profile'] = False
                dict['children'] = []
                res.append(dict)
            if len(top_catalog.datasets) > 0:
                gen_dict = self.aux_get_gliders_layers(top_catalog)
                for i in gen_dict:
                    res.append(i)
        else:
            print("hola 3")
            gen_dict = self.aux_get_gliders_layers(top_catalog)
            for i in gen_dict:
                res.append(i)
        return res

    def aux_get_gliders_layers(self,catalog):
        for idx, data in enumerate(catalog.datasets.values()):
            dict = {}
            dict['id'] = str(data)
            dict['name'] = str(data)
            dict['url'] = data.access_urls['OPENDAP']
            dict['url_download'] = data.access_urls['HTTPServer']
            dict['is_file'] = True
            dict['children'] = []
            yield dict