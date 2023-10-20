from dotenv import load_dotenv
from google.cloud import storage
import os

def transcribe_gcs(gcs_uri: str) -> str:
"""Asynchronously transcribes the audio file specified by the gcs_uri.

Args:
gcs_uri: The Google Cloud Storage path to an audio file.

Returns:
The generated transcript from the audio file provided.
"""
from google.cloud import speech

client = speech.SpeechClient()

audio = speech.RecognitionAudio(uri=gcs_uri)
config = speech.RecognitionConfig(
encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
sample_rate_hertz=44100,
language_code="ru-RU",
audio_channel_count=2 
)

operation = client.long_running_recognize(config=config, audio=audio)

print("Waiting for operation to complete...")
#response = operation.result(timeout=90)
response = operation.result(timeout=200)

transcript_builder = []
# Each result is for a consecutive portion of the audio. Iterate through
# them to get the transcripts for the entire audio file.
for result in response.results:
# The first alternative is the most likely one for this portion.
transcript_builder.append(f"\n{result.alternatives[0].transcript}")
#transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")

transcript = "".join(transcript_builder)
print(transcript)

return transcript

# Todo: Create folder in bucket with date to place the results


def run_transcibe_on_each_file(bucket_name):

storage_client = storage.Client()

# Note: Client.list_blobs requires at least package version 1.17.0.
blobs = storage_client.list_blobs(bucket_name)

# Note: The call returns a response only when the iterator is consumed.
for blob in blobs:
if blob.name.endswith(".flac"):
print("\nTranscribing the file: " + blob.name)
transcribe_gcs(f"{google_bucket_path}/{blob.name}")

if __name__ == "__main__":
load_dotenv() # take environment variables from .env.
google_bucket_path = os.environ["GOOGLE_BUCKET"]
bucket_name = os.environ["BUCKET_NAME"]

run_transcibe_on_each_file(bucket_name)
