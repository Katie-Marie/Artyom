# Artyom
Batch transcribe and translate audio files
This project takes a batch of mp3 files and transcribes them into their native language as well as creating a translation into english. 

Intended use of this tool: about once a week download a bunch of podcasts in foreign languages, upload them to Google bucket and run this script to transcribe them. 
After listening to the podcasts I can then come back and read the transcripts to see what I missed.

To use this tool you will require/need to:
- a Google Cloud Project
- a Google Service Account with billing enabled
- enable the Speech-to-Text AP 
- create a Google Storage bucket with Speech Administrator role
- create a python virtual environment to separate dependencies 
For detailed steps to setting up the Speech-to-Text API you can refer to this link but only follow first part (most of it is irrelevant as we are transcribing files greater than 60 seconds):
https://codelabs.developers.google.com/codelabs/cloud-speech-text-python3/#1

You will also need to setup authentication using Application Default Credentials (ADC) (because we are accessing the project outside of the Cloud Shell). 
Steps to creating your credential file:
https://cloud.google.com/docs/authentication/provide-credentials-adc

You will also need to create .env and edit it:
# Development settings
GOOGLE_BUCKET="gs://path/to/bucket"
BUCKET_NAME = "bucket_name"


Project Uses:
Often there will be an interesting podcast in the language you are trying to learn but no transcripts/translations available. 
The tool is also useful for learning languages where there is limited freely available materials beyond the beginner courses. (I found this to be the case in trying to learn Hebrew and Maori). 
This is a tool suitable for people at an intermediate level of a language, who are unconcerned with making mistakes and just want to consume more interesting content in their target language. 

Note: transcribe.py script uses Google Cloud Speech-to-Text API and as such is an imperfect transciption of the audio file. 
Note: it may take a while to do the transcription/translation depending on how heavily the batch to transcribe is.

For best results, the audio source should be captured and transmitted using a lossless encoding (FLAC or LINEAR16).
So step one is to convert to FLAC using ffmpeg: 
ffmpeg -i 2019-03-02-10-00-00.mp3 -c:a flac 2019-03-02-10-00-00.flac

Create python virtual env and then activate:
source venv-transcribe/bin/activate

Todo later: put the following in requirements.txt:

`pip install python-dotenv`
`pip install google-cloud-storage`

Asynchronous speech recognition starts a long running audio processing operation. Use asynchronous speech recognition to transcribe audio that is longer than 60 seconds.

To use asynchronous speech recognition to transcribe audio longer than 60 seconds, you must have your data saved in a Google Cloud Storage bucket.

You can retrieve the results of the operation using the google.longrunning.Operations method. Results remain available for retrieval for 5 days (120 hours). You also have the option of uploading your results directly to a Google Cloud Storage bucket.