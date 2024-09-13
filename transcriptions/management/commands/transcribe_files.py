# transcriptions_project/transcriptions/management/commands/transcribe_files.py

import sys
import asyncio
import websockets
import wave
import pymysql
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argostranslate.package
import argostranslate.translate
from transformers import pipeline
from pyannote.audio import Pipeline
from django.core.management.base import BaseCommand
from transcriptions.models import Transcription

# WebSocket server URI
WS_URI = 'ws://localhost:2700'

# Directory to monitor
WATCH_DIRECTORY = '/var/lib/test/'

# Initialize the sentiment analysis pipeline
sentiment_analysis = pipeline("sentiment-analysis")

# Initialize the speaker diarization pipeline
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="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")

def translate_text(text):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next(filter(lambda x: x.code == "hi", installed_languages), None)
    to_lang = next(filter(lambda x: x.code == "en", installed_languages), None)

    if from_lang and to_lang:
        translation = from_lang.get_translation(to_lang).translate(text)
        return translation
    return ""

class TranscriptionHandler(FileSystemEventHandler):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.wav'):
            print(f'New WAV file detected: {event.src_path}')
            self.loop.run_until_complete(self.transcribe_translate_and_save(event.src_path))

    async def transcribe_translate_and_save(self, file_path):
        async with websockets.connect(WS_URI) as websocket:
            wf = wave.open(file_path, "rb")
            await websocket.send(json.dumps({"config": {"sample_rate": wf.getframerate()}}))
            buffer_size = int(wf.getframerate() * 0.2)  # 0.2 seconds of audio
            transcript = ""
            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break
                await websocket.send(data)
                response = await websocket.recv()
                result = json.loads(response)
                if 'text' in result:
                    transcript += result['text'] + ' '
                print(response)
            await websocket.send('{"eof" : 1}')
            final_response = await websocket.recv()
            final_result = json.loads(final_response)
            if 'text' in final_result:
                transcript += final_result['text']
            print(final_response)
            
            # Translate the transcript
            translation = translate_text(transcript)

            # Perform sentiment analysis
            sentiment_result = sentiment_analysis(transcript)
            sentiment_score = sentiment_result[0]['score']

            # Perform speaker diarization
            diarization = diarization_pipeline(file_path)
            speakers = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.append((turn, speaker))

            # Save the result in the database
            self.save_to_db(file_path, transcript, translation, sentiment_score, speakers)

    def save_to_db(self, file_path, transcript, translation, sentiment_score, speakers):
        transcription = Transcription(
            file_name=os.path.basename(file_path),
            transcription=transcript,
            translation=translation,
            sentiment_score=sentiment_score,
            speakers=json.dumps(speakers)
        )
        transcription.save()
        print(f'Transcription, translation, sentiment score, and speakers saved to database for file: {file_path}')

class Command(BaseCommand):
    help = 'Monitors a directory for new audio files and processes them'

    def handle(self, *args, **kwargs):
        # Set up the directory observer
        event_handler = TranscriptionHandler()
        observer = Observer()
        observer.schedule(event_handler, WATCH_DIRECTORY, recursive=False)
        observer.start()
        print(f'Started monitoring directory: {WATCH_DIRECTORY}')

        self.stdout.write(self.style.SUCCESS('Files have been transcribed'))

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

