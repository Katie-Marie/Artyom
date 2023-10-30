from dotenv import load_dotenv
from google.cloud import storage
from google.cloud import translate
import os
import argparse


parser = argparse.ArgumentParser(description='Transcribe audio files in a bucket')
parser.add_argument('language_code', metavar='L', type=str, nargs='+',
                    help='Code for the language of the original audio. E.g Russian="ru-RU", English="en-US", Hebrew="iw-IL", German="de-DE".  Lookup speech-to-text-supported-languages')


args = parser.parse_args()
language_code = args.language_code[0]
print('Transcribing from '+ language_code + ' to English')

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
        language_code=language_code, 
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

    # Put translation in a txt file
    english_trans_file = open(r'english_trans.txt', 'w')
    english_trans_file.write(translation)
    english_trans_file.close()
    #print(transcript)

    # Alternatively I could Write an Event-driven cloud function to detect when a new output file is created in the bucket and run a python script to translate it.
    # https://cloud.google.com/functions/docs/calling/storage#python
    # https://cloud.google.com/functions/docs/calling/storage#functions-calling-storage-python
    # https://cloud.google.com/storage/docs/pubsub-notifications
    # https://cloud.google.com/storage/docs/pubsub-notifications#_Event_types



from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )



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
            trans_output_file = blob.name.replace(".flac", "_english_trans.txt")
            transcribe_gcs(f"{google_bucket_path}/{blob.name}", output_file_name=f"{google_bucket_path}/{output_file}" )
            # copy translation_file to the bucket via api
            # https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
            upload_blob(bucket_name, 'english_trans.txt', trans_output_file)



if __name__ == "__main__":

    load_dotenv() # take environment variables from .env.
    bucket_name = os.environ["BUCKET_NAME"]
    PROJECT_ID = os.environ.get("PROJECT_ID", "") # Your GCP Project ID
    PARENT = f"projects/{PROJECT_ID}"

    run_transcibe_on_each_file(bucket_name)
 
