import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from netCDF4 import num2date, date2num, date2index


class Plots:

    def init_generation_data(self, dataForm):
        collections_urls = []
        ds = xr.open_dataset(dataForm["URL"], decode_times=False)
        # List data_var without QC variables
        my_filtered = filter(lambda vars: 'QC' not in vars, list(ds.data_vars))
        # Iterate for this list without QC
        for varirable_filter in list(my_filtered):
            print("Variable: ", varirable_filter, " - Coordenadas: ", list(ds[varirable_filter].coords))
            dict_var = {}
            # print(ds[varirable_filter].coords.dims.size)
            # Iterate for each coordinate from variable. exp: TEMP : (TIME, DEPTH)
            for coord in list(ds[varirable_filter].coords):
                # If coord (for example, TIME or DEPTH) is in dataForm (DataRequest from Frontend Form )
                # Method por extract data for coord
                dict_var[coord] = self.extract_data_according_variable(dataForm, coord, ds)
            data_isel = ds[varirable_filter].isel(dict_var)
            name_property = "% s % s" % ("PROPERTY_", varirable_filter)
            dict_var[name_property] = data_isel.values
            ## Mostrar url con el yield generator
            urls_plots = self.setting_axis_plot(dict_var, ds, dataForm)
            for url in urls_plots:
                collections_urls.append(url)
        return collections_urls

    def setting_axis_plot(self, dict_data, ds, dataForm):
        x_axis = None
        y_axis = None
        x_label = None
        y_label = None
        label_name = None
        label_data = None
        collection_date = None
        indexes = None
        for key, value in dict_data.items():
            # print(key, '->', value.flatten())
            if len(value.flatten()) > 1:
                if key == 'TIME':
                    my_date_year_month = np.array(
                        [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(ds[key].values[value], ds[key].units)])
                    filter_date = np.array(
                        [date.strftime('%Y-%m-%d') for date in num2date(ds[key].values[value], ds[key].units)])
                    arr = []
                    for date in list(set(filter_date)):
                        arr.append(np.where(filter_date == date))
                    indexes = arr
                    fechas = set((fecha.split(' ')[0] for fecha in list(my_date_year_month)))
                    collection_date = [[valor for valor in list(my_date_year_month) if valor.startswith(fecha)] for
                                       fecha in fechas]
                    # print(new_list)
                    x_axis = my_date_year_month
                    x_label = key
                elif "PROPERTY" in key:
                    if x_axis is not None:
                        y_axis = value.flatten()
                        y_label = key
                    else:
                        x_axis = value.flatten()
                        x_label = key
                else:
                    y_axis = value.flatten()
                    y_label = key
            else:
                if key == 'TIME':
                    my_date_year_month = np.array(
                        [date.strftime('%Y-%m-%d %H:%M:%S') for date in num2date(ds[key].values[value], ds[key].units)])
                    filter_date = np.array(
                        [date.strftime('%Y-%m-%d') for date in num2date(ds[key].values[value], ds[key].units)])
                    arr = []
                    for date in list(set(filter_date)):
                        arr.append(np.where(filter_date == date))
                    indexes = arr
                    fechas = set((fecha.split(' ')[0] for fecha in list(my_date_year_month)))
                    collection_date = [[valor for valor in list(my_date_year_month) if valor.startswith(fecha)] for
                                       fecha in
                                       fechas]
                    label_data = my_date_year_month
                else:
                    label_data = ds[key].values[value]
                label_name = key

        plots = self.generate_plot(x_axis, y_axis, label_data, ds, collection_date, indexes, dataForm, x_label, y_label,
                                   label_name)
        for plot in plots:
            yield plot

    def generate_plot(self, xaxis, yaxis, label_data, ds, collection_date, indexes, dataForm, x_label, y_label, label_name):
        if len(collection_date) > 1:
            for x_axis, y_axis in zip(collection_date, indexes):
                print(x_axis, yaxis[y_axis])
                plt.plot(x_axis, yaxis[y_axis])
                plt.suptitle(dataForm["NAME"], fontsize=12)
                plt.title("% s % s %s %s %s %s" % ("LATITUDE:",
                                                   dataForm["LATITUDE"],
                                                   "LONGITUDE:",
                                                   dataForm["LONGITUDE"],
                                                   label_name,
                                                   label_data
                                                   ),
                          loc='left',
                          fontsize=8,
                          fontweight='bold',
                          style='italic',
                          family='monospace',
                          )
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                plt.xticks(rotation=90)
                plt.tight_layout()
                f = io.BytesIO()
                plt.savefig(f, format="png", dpi=72)
                f.seek(0)
                encode = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
                f.close()
                plt.close()
                yield encode
                # plt.show()
        else:
            plt.plot(xaxis, yaxis)
            plt.suptitle(dataForm["NAME"], fontsize=12)
            plt.title("% s % s %s %s %s %s" % ("LATITUDE:",
                                               dataForm["LATITUDE"],
                                               "LONGITUDE:",
                                               dataForm["LONGITUDE"],
                                               label_name,
                                               label_data),
                      loc='left',
                      fontsize=8,
                      fontweight='bold',
                      style='italic',
                      family='monospace',
                      )
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.tight_layout()
            f = io.BytesIO()
            plt.savefig(f, format="png", dpi=72)
            f.seek(0)
            encode = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
            f.close()
            plt.close()
            yield encode
            # plt.show()

    def extract_data_according_variable(self, dataForm, coord, ds):
        if coord == 'TIME':
            my_date_year_month = np.array(
                [date.strftime('%Y-%m') for date in num2date(ds[coord].values, ds[coord].units)])
            index_values = np.where(my_date_year_month == dataForm[coord])
            return index_values[0]
        else:
            return np.arange(len(ds[coord].values))