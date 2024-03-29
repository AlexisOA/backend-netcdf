from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from thredds_api.usecase import thredds_usecase as thredds_uc, datafiles_usecase as datafiles, thredds_gliders as thredds_gliders
from thredds_api import serializers
from rest_framework import status
from django.http import JsonResponse, HttpResponse


class CatalogThredds(APIView):

    def get(self, request, format=None):
        """Retornar json de capas de la web Thredds"""
        url = 'http://data.plocan.eu/thredds/catalog.xml'
        res = thredds_uc.ThreddsCatalog().access_to_catalog_thredds(url)
        return Response(res)

class FixedObsLayers(APIView):
    serializer_class = serializers.URLSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            res = thredds_uc.ThreddsCatalog().get_fixedobs_layers_from_thredds(url)
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
        res = thredds_uc.ThreddsCatalog().get_fixedobs_layers_from_thredds(url)
        init_dict = {'id': 'Thredds PLOCAN', 'name': 'Fixed observatories', 'is_file': False, 'url': url, 'children': res}
        return Response(init_dict)

class GlidersLayers(APIView):

    serializer_class = serializers.URLSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            res = thredds_uc.ThreddsCatalog().get_gliders_layers(url)
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
        res = thredds_uc.ThreddsCatalog().get_gliders_layers(url)
        init_dict = {'id': 'Thredds PLOCAN', 'name': 'Autonomous systems', 'is_file': False, 'url': url, 'children': res}
        return Response(init_dict)

class GlidersDataset(APIView):
    # serializer_class_3 = serializers.URLArraySerializer
    serializer_class = serializers.URLSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            # url_download = serializer.validated_data.get('url_download')
            # res = thredds_gliders.AutonomousSystems().get_dataset_glider(url)
            res = thredds_gliders.AutonomousSystems().get_dataset_glider_coordinates(url)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class GlidersDatasetVariable(APIView):
    # serializer_class = serializers.GliderVariableDataset
    serializer_class = serializers.GliderVariableDatasetNew
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            name_variable = serializer.validated_data.get('name_variable')
            # res = thredds_gliders.AutonomousSystems().get_data_properties_from_glider(url, name_variable)

            date_init = serializer.validated_data.get('date_init')
            date_fin = serializer.validated_data.get('date_fin')
            print(url, name_variable, date_init, date_fin)
            res = thredds_gliders.AutonomousSystems().get_data_properties_from_glider_two(url, name_variable, date_init, date_fin)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class DataThredds(APIView):
    serializer_class = serializers.URLSSerializer
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
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            url_download = serializer.validated_data.get('url_download')
            # res = thredds_uc.ThreddsCatalog().get_marker_coords_from_thredds(url)
            res = thredds_uc.ThreddsCatalog().get_info_file_for_popup(url, url_download)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
class DataThreddsProfiles(APIView):
    serializer_class_3 = serializers.URLArraySerializer

    def post(self, request):
        serializer = self.serializer_class_3(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            url_download = serializer.validated_data.get('url_download')
            res = thredds_uc.ThreddsCatalog().get_info_file_for_popup_profiles(url, url_download)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class DataForm(APIView):
    serializer_class_2 = serializers.URLSSerializer

    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class_2(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            url_download = serializer.validated_data.get('url_download')
            # res = thredds_uc.ThreddsCatalog().get_data_select(url, url_download)
            res = datafiles.DataFiles().get_data_select_antiguo(url, url_download)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

class DataFormProfiles(APIView):
    serializer_class_2 = serializers.URLArraySerializer

    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class_2(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            url_download = serializer.validated_data.get('url_download')
            # res = thredds_uc.ThreddsCatalog().get_data_select(url, url_download)
            res = datafiles.DataFiles().get_profiles_shipbased(url, url_download)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )




class CSVFile(APIView):
    serializer_class = serializers.URLSerializer

    def post(self, request):
        """POST for local files"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            df = thredds_uc.ThreddsCatalog().get_file_as_dataframe(url)
            name_csv = url.split('/')[-1].replace(".nc", ".csv")
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s' % name_csv
            df.to_csv(path_or_buf=response, decimal=',', sep=';', index=False, float_format='%.4f')
            return response
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
