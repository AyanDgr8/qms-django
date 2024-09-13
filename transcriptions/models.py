# transcriptions_project/transcriptions/models.py

from django.db import models

class Transcription(models.Model):
    file_name = models.CharField(max_length=255)
    date_time = models.DateTimeField(null=True, blank=True)
    agent_transcription = models.TextField(null=True, blank=True)
    agent_translation = models.TextField(null=True, blank=True)
    agent_sentiment_score = models.FloatField(null=True, blank=True)
    customer_transcription = models.TextField(null=True, blank=True)
    customer_translation = models.TextField(null=True, blank=True)
    customer_sentiment_score = models.FloatField(null=True, blank=True)
    abusive_count = models.IntegerField(null=True, blank=True)
    contains_financial_info = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'transcriptions'  # Make sure this matches the actual table name
