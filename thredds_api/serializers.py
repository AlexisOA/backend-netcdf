from rest_framework import serializers


class URLSerializer(serializers.Serializer):
    url = serializers.URLField()

class URLSSerializer(serializers.Serializer):
    url = serializers.URLField()
    url_download = serializers.URLField()

class GliderVariableDataset(serializers.Serializer):
    url = serializers.URLField()
    name_variable = serializers.CharField()
class GliderVariableDatasetNew(serializers.Serializer):
    url = serializers.URLField()
    name_variable = serializers.CharField()
    date_init = serializers.CharField()
    date_fin = serializers.CharField()


class URLArraySerializer(serializers.Serializer):
    url = serializers.ListField()
    url_download = serializers.ListField()


class NameSerializer(serializers.Serializer):
    name = serializers.CharField()


class FormPlotSerializer(serializers.Serializer):
    dataForm = serializers.DictField()
