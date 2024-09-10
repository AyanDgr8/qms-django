from django.db import models

class Transcription(models.Model):
    file_name = models.CharField(max_length=255)
    date_time = models.DateTimeField(auto_now_add=True)
    transcription = models.TextField()
    translation = models.TextField()
    sentiment_score = models.FloatField()
    speakers = models.TextField()

    def __str__(self):
        return self.file_name
