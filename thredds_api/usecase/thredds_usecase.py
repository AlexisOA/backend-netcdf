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
class ThreddsCatalog:

    def access_to_catalog_thredds(self, url):
        base_dir = settings.BASE_DIR
        new_dir = str(base_dir).replace("\\", "/") + "/thredds_api/files"
        path = str(new_dir) + '/thredds_service.json'
        if not os.path.exists(path):
            print("Generando...")
            dict_thredds = {}
            url_root = "http://data.plocan.eu/thredds/catalog.xml"
            dict_thredds['id'] = "Thredds PLOCAN"
            dict_thredds['name'] = "Thredds PLOCAN"
            dict_thredds['url'] = "http://data.plocan.eu/thredds/catalog.xml"
            dict_thredds['is_file'] = False
            dict_thredds['children'] = []
            catalog_complete = self.generate_json_catalogs_thredds(url_root, dict_thredds)
            profiles_shipbased = self.generate_profiles_from_shipbased(catalog_complete)
            result = self.update_shipbased_profiles(catalog_complete, profiles_shipbased)
            print(type(result))
            with open(path, 'w') as fp:
                json.dump(result, fp)
            return result
        else:
            print("Cargando file")
            with open(path) as json_file:
                data = json.load(json_file)
                return data

    def update_shipbased_profiles(self,catalog, new_children):
        for idx, obj in enumerate(catalog["children"]):
            for data in obj["children"]:
                if data["is_profile"]:
                    data["children"] = new_children
                    break
        return catalog

    def generate_profiles_from_shipbased(self, res):
        arr = []
        for obj in res["children"]:
            for data in obj["children"]:
                if data["is_profile"]:
                    groups_opendap = {}
                    groups_http = {}
                    for ship in data["children"]:
                        if ship['name'] == "UnderRevision": continue
                        n = str(ship["name"]).split('_')[2]

                        if n in groups_opendap:
                            groups_opendap[n].append(ship["url"])
                            groups_http[n].append(ship["url_download"])
                        else:
                            groups_opendap[n] = [ship["url"]]
                            groups_http[n] = [ship["url_download"]]
                    for key, value in groups_opendap.items():
                        if "2009" in key: continue
                        dict_group = {}
                        url_opendap = value[0]
                        name_id = url_opendap[url_opendap.rindex('/') + 1:url_opendap.rindex('CTD') + 3]
                        dict_group['id'] = name_id
                        dict_group['name'] = name_id
                        dict_group['is_file'] = True
                        dict_group['is_profile'] = True
                        dict_group['children'] = []
                        dict_group['url'] = value
                        dict_group['url_download'] = groups_http[key]
                        arr.append(dict_group)
                    return arr

    def generate_json_catalogs_thredds(self, url, dict_parameter):
        root_catalog = TDSCatalog(url)
        if len(root_catalog.catalog_refs) > 0:
            for catalog in root_catalog.catalog_refs:
                thredds_json = {}
                # print(type(root_catalog.catalog_refs[catalog]))
                if catalog == 'Test': continue
                next_url = root_catalog.catalog_refs[catalog].href
                thredds_json["name"] = catalog
                thredds_json["id"] = catalog
                thredds_json["url"] = next_url
                thredds_json["is_file"] = False
                if catalog == 'ship-based':
                    thredds_json["is_profile"] = True
                else:
                    thredds_json["is_profile"] = False
                thredds_json["children"] = []
                for ds in threddsclient.crawl(next_url):
                    url_file = next_url.replace("catalog.xml", ds.name)
                    index = url_file.find("catalog")
                    url = url_file[:index] + 'dodsC' + url_file[index:]
                    url_download = url_file[:index] + 'fileServer' + url_file[index:]
                    child = {}
                    child["name"] = ds.name
                    child["id"] = catalog + "/" + ds.name
                    child["url"] = url.replace("catalog", "")
                    child["url_download"] = url_download.replace("catalog", "")
                    child["is_file"] = True
                    thredds_json["children"].append(child)
                self.generate_json_catalogs_thredds(next_url, thredds_json)
                dict_parameter["children"].append(thredds_json)
        else:
            return dict_parameter
        return dict_parameter

    def get_info_file_for_popup_profiles(self, url_arrays, urlDownload_arrays):
        latitude_y = np.array([])
        longitude_x = np.array([])
        dict_site = {}
        first_file = url_arrays[0]
        for url in url_arrays:
            f = netCDF4.Dataset(url)
            latitude_y = np.append(latitude_y, f.getncattr('geospatial_lat_min'), axis=None)
            longitude_x = np.append(longitude_x, f.getncattr('geospatial_lon_max'), axis=None)
        center_circle = [(np.max(longitude_x) + np.min(longitude_x))/2, (np.max(latitude_y) + np.min(latitude_y))/2]
        dict_site['url'] = url_arrays
        dict_site['url_download'] = urlDownload_arrays
        f = netCDF4.Dataset(first_file)
        date_split = f.getncattr('time_coverage_start').split('-')
        date_month = f"{date_split[0]}/{date_split[1]}"
        dict_site['Description'] = f.getncattr('summary')
        dict_site['Area'] = f.getncattr('area')
        dict_site['Datefrom'] = date_month
        dict_site['Dateto'] = date_month
        dict_site['Name'] = "Profile files"
        dict_site['Latitude'] = center_circle[1]
        dict_site['Longitude'] = center_circle[0]
        dict_site['isprofile'] = True
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
        dict_site['isprofile'] = False
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
        groups_opendap = {}
        groups_http = {}
        print(catalog.datasets.values())
        for data in catalog.datasets.values():
            n = str(data).split('_')[2]
            if n in groups_opendap:
                groups_opendap[n].append(data.access_urls['OPENDAP'])
                groups_http[n].append(data.access_urls['HTTPServer'])
            else:
                groups_opendap[n] = [data.access_urls['OPENDAP']]
                groups_http[n] = [data.access_urls['HTTPServer']]

        for key, value in groups_opendap.items():
            if "2009" in key: continue
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