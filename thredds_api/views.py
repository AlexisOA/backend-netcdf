from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from thredds_api.usecase import thredds_usecase as thredds_uc
from thredds_api.usecase import plots_usecase as plots_uc
from thredds_api import serializers
from rest_framework import status
from django.http import JsonResponse
import time
import matplotlib.pyplot as plt
# Create your views here.
import xarray as xr
import matplotlib.pyplot as plt
import sys
import numpy as np
import io
import base64

class LayersJson(APIView):

    serializer_class = serializers.URLSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            res = thredds_uc.ThreddsCatalog().get_first_layer_from_thredds(url)
            # res = thredds_uc.ThreddsCatalog.get_layers_test(url)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, format=None):
        """Retornar json de capas de la web Thredds"""
        url = 'http://data.plocan.eu/thredds/catalog.xml'
        thredds_catalog = thredds_uc.ThreddsCatalog()
        # res = thredds_catalog.get_layers_test()
        res = thredds_uc.ThreddsCatalog().get_first_layer_from_thredds(url)
        init_dict = {'id': 'Thredds PLOCAN', 'name': 'Thredds PLOCAN', 'is_file': False, 'url': url, 'children': res}
        return Response(init_dict)



class DataThredds(APIView):
    serializer_class = serializers.URLSerializer
    serializer_class_2 = serializers.NameSerializer
    serializer_class_3 = serializers.URLArraySerializer

    # def post(self, request):
    #     print("EN EL POST DE COORDINATES")
    #     serializer = self.serializer_class_3(data=request.data)
    #     if serializer.is_valid():
    #         url = serializer.validated_data.get('url_array')
    #         # res = thredds_uc.ThreddsCatalog().get_marker_coords_from_thredds(url)
    #         res = thredds_uc.ThreddsCatalog().get_marker_array_coords_from_thredds(url)
    #         return Response(res)
    #     else:
    #         return Response(
    #             serializer.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    def post(self, request):
        print("EN EL POST DE COORDINATES")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            # res = thredds_uc.ThreddsCatalog().get_marker_coords_from_thredds(url)
            res = thredds_uc.ThreddsCatalog().get_data_from_file_to_map(url)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    # def post(self, request):
    #     """POST for local files"""
    #     serializer = self.serializer_class_2(data=request.data)
    #     if serializer.is_valid():
    #         name = serializer.validated_data.get('name')
    #         print("name: ", name)
    #         res = thredds_uc.ThreddsCatalog().get_coords_local_files(name)
    #         return Response(res)
    #     else:
    #         return Response(
    #             serializer.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #     )

class GraphicThredds(APIView):

    serializer_class_2 = serializers.NameSerializer

    # def get(self, request):
    #     thredds_cat = thredds_uc.ThreddsCatalog()
    #     json_data = thredds_cat.get_graphic_from_nc_file()
    #     return JsonResponse(json_data)


    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class_2(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            print("name: ", name)
            res = thredds_uc.ThreddsCatalog().get_graphic_from_local_file(name)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
        )


class DataForm(APIView):
    serializer_class_2 = serializers.NameSerializer
    # def post(self, request):
    #     """POST for local files"""
    #     serializer = self.serializer_class_2(data=request.data)
    #     if serializer.is_valid():
    #         name = serializer.validated_data.get('name')
    #         res = thredds_uc.ThreddsCatalog().get_data_plot_forms(name)
    #         return Response(res)
    #     else:
    #         return Response(
    #             serializer.errors,
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class_2(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            res = thredds_uc.ThreddsCatalog().get_data_select(name)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class DataFormChoose(APIView):
    serializer_class = serializers.FormPlotSerializer

    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            dataForm = serializer.validated_data.get('dataForm')
            res = plots_uc.Plots().init_generation_data(dataForm)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
        )

