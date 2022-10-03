from rest_framework import serializers


class URLSerializer(serializers.Serializer):
    url = serializers.URLField()


class URLArraySerializer(serializers.Serializer):
    url_array = serializers.ListField()


class NameSerializer(serializers.Serializer):
    name = serializers.CharField()


class FormPlotSerializer(serializers.Serializer):
    dataForm = serializers.DictField()
