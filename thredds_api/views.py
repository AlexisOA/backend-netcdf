from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from thredds_api.usecase import thredds_usecase as thredds_uc
from thredds_api import serializers
from rest_framework import status
import time
# Create your views here.


class LayersJson(APIView):

    serializer_class = serializers.URLSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            res = thredds_uc.ThreddsCatalog().get_first_layer_from_thredds(url)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, format=None):
        """Retornar json de capas de la web Thredds"""
        url = 'http://data.plocan.eu/thredds/catalog.xml'
        res = thredds_uc.ThreddsCatalog().get_first_layer_from_thredds(url)
        return Response({'id': 'Thredds PLOCAN', 'name': 'Thredds PLOCAN', 'url': url, 'children': res})



class DataThredds(APIView):
    serializer_class = serializers.URLSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data.get('url')
            res = thredds_uc.ThreddsCatalog().get_marker_coords_from_thredds(url)
            return Response(res)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

