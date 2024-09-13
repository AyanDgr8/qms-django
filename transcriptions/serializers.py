# transcriptions_project/transcriptions/serializers.py

from rest_framework import serializers
from .models import Transcription

class TranscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transcription model, converting model instances
    into JSON format for API responses.
    """
    class Meta:
        model = Transcription
        # Specify the fields to be serialized, you can also list the fields explicitly
        fields = '__all__'  # Serializes all fields in the Transcription model
