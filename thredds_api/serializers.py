from rest_framework import serializers


class URLSerializer(serializers.Serializer):
    url = serializers.URLField()

class NameSerializer(serializers.Serializer):
    name = serializers.CharField()
