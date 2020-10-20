from rest_framework import serializers
from blur_del.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('title', 'img', 'blurInt', 'keysession', "outputPath")
