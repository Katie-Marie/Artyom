# Artyom
Artyom is a tool which takes a batch of audio files and transcribes them into their native language as well as creating a translation into english. 

Intended use of this tool: After downloading a bunch of podcasts in a foreign language, run this script to create transcriptions and translations in a google bucket. 
Often there will be an interesting podcast in the language you are trying to learn but no transcripts/translations available. It's also useful when you are trying to learn a language with very few learning materials available. 

To use this tool you will require:
- a Google Cloud Project
- a Google Service Account with billing enabled

You will need to:
- enable the Speech-to-Text API and Translate API
- create a Google Storage bucket with Speech Administrator role
- create a python virtual environment to separate dependencies   
For detailed steps to setting up the Speech-to-Text API you can refer to this link but only follow first part (most of it is irrelevant as we are transcribing files greater than 60 seconds):
https://codelabs.developers.google.com/codelabs/cloud-speech-text-python3/#1

You will also need to setup authentication using Application Default Credentials (ADC) (because we are accessing the project outside of the Cloud Shell). 
Steps to creating your credential file:
https://cloud.google.com/docs/authentication/provide-credentials-adc

You will also need to create .env and edit it:  
GOOGLE_BUCKET="gs://path/to/bucket"  
BUCKET_NAME = "bucket_name"    
PROJECT_ID = "google_project_id"


Then create a local folder populated with, for example, dowloaded podcasts in mp3 format.

Note: transcribe.py script uses Google Cloud Speech-to-Text API and as such is an imperfect transciption of the audio file. 
Note: it may take a while to do the transcription/translation depending on how heavy the batch to transcribe is.

Create python virtual env and then activate:
source venv-transcribe/bin/activate

Todo later: put the following in requirements.txt:

`pip install python-dotenv`  
`pip install google-cloud-storage`   
`pip install google-cloud-speech`  
`pip install ipython google-cloud-translate`  


For best results, the audio source should be captured and transmitted using a lossless encoding (FLAC or LINEAR16).
So step one is to take all the raw mp3 audio files and convert to FLAC using ffmpeg:   
ffmpeg -i filename.mp3 -c:a flac output_filename.flac


Asynchronous speech recognition starts a long running audio processing operation. Asynchronous speech recognition is used to transcribe audio that is longer than 60 seconds.
To use asynchronous speech recognition to transcribe audio longer than 60 seconds, you must have your data saved in a Google Cloud Storage bucket.

 Text is translated using the Neural Machine Translation (NMT) model. If the NMT model is not supported for the requested language translation pair, the Phrase-Based Machine Translation (PBMT) model is used.


Run the command   
`python transcribe.py -h`  
to see usage.

(venv-transcribe) pwd$ python3 transcribe.py "ru-RU" '/home/usr/Audio/...'

I have used this tool successfully with files shorter than 30 mins. It's super cool opening up the files and seeing the transcription and translations.
