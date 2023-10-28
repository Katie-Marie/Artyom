from dotenv import load_dotenv
from google.cloud import storage

from google.cloud import translate
import os


def transcribe_gcs(gcs_uri: str, output_file_name) -> str:
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
        language_code="ru-RU",  # Change to your language of interest
        audio_channel_count=2 
    )
    # Create a TranscriptOutputConfig object
    google_bucket_path = os.environ["GOOGLE_BUCKET"]
    transcript_output_config =  speech.TranscriptOutputConfig(gcs_uri=output_file_name)

    request = speech.LongRunningRecognizeRequest(
    config=config,
    audio=audio,
    output_config=transcript_output_config
    )

    operation = client.long_running_recognize(request=request)

    print("Waiting for operation to complete...")
    #response = operation.result(timeout=90)
    response = operation.result(timeout=200)

    transcript_builder = []
    translation_builder = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
    # The first alternative is the most likely one for this portion.
        transcript_builder.append(f"\n{result.alternatives[0].transcript}")
        translation_builder.append(f"\n{translate_text(result.alternatives[0].transcript, 'en').translated_text}")

    transcript = "".join(transcript_builder)
    translation = "".join(translation_builder)
    print(transcript)

    return translation




def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]


def run_transcibe_on_each_file(bucket_name):

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    google_bucket_path = os.environ["GOOGLE_BUCKET"]

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        if blob.name.endswith(".flac"):
            print("\nTranscribing the file: " + blob.name)
            output_file = blob.name.replace(".flac", "_output.txt")
            #transcribe_gcs(f"{google_bucket_path}/{blob.name}", f"{google_bucket_path}/{blob.name}" )
            transcribe_gcs(f"{google_bucket_path}/{blob.name}", output_file_name=f"{google_bucket_path}/{output_file}" )


if __name__ == "__main__":

    load_dotenv() # take environment variables from .env.
    bucket_name = os.environ["BUCKET_NAME"]
    PROJECT_ID = os.environ.get("PROJECT_ID", "") # Your GCP Project ID
    PARENT = f"projects/{PROJECT_ID}"
    

    run_transcibe_on_each_file(bucket_name)
    #run_transcibe_on_each_file(bucket_name)
