from rest_framework import serializers
from .models import Image, Annotation

class ImageSerializer(serializers.ModelSerializer):
    annotations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Image
        fields = '__all__'

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = '__all__'
