# beat creation script

from pydub import AudioSegment
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME

boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('twilio-rapper')
    key.key = 'test'
    key.get_contents_from_filename('')

def get_AudiSegment_from_s3(index):
    '''
    Files in beat_creator are as follows:
    1.wav -- hihat.wav
    2.wav -- snare.wav
    3.wav -- bass.wav
    4.wav -- hihatsnare.wav
    5.wav -- hihatbass.wav
    6.wav -- snarebass.wav
    7.wav -- all3.wav
    8.wav -- rest.wav
    '''
    key = Key(bucket)  
    file_name = '%d.wav' % index
    key.key = 'beat_creator/{file_name}'.format(file_name=file_name)
    key.get_contents_to_filename(file_name)
    return AudioSegment.from_wav(file_name)


def send_beat_to_s3(filename):
    key = Key(bucket)
    key.key = 'finished_beats/{filename}'.format(filename=filename)
    key.set_contents_from_filename(filename)


def create_beat(indices):
    samples = [None]*9
    unique_indices = set(indices)
    for i in unique_indices:
        samples[i] = get_AudioSegment_from_s3(i)
    beat = (samples[indices[0]] + samples[indices[1]] + samples[indices[2]] + samples[indices[3]] + samples[indices[4]] + 
            samples[indices[5]] + samples[indices[6]] + samples[indices[7]])
    name = (str(indices[0]) + str(indices[1]) + str(indices[2]) + str(indices[3]) + str(indices[4]) + 
        str(indices[5]) + str(indices[6]) + str(indices[7]) + '.wav') 
    beat.export(name, format="wav")
    send_beat_to_s3(name)
    return name