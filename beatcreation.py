# beat creation script

from pydub import AudioSegment
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME

boto_conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
bucket = boto_conn.get_bucket('twilio-rapper')
s3_url_format = 'https://twilio-rapper.s3.amazonaws.com/{end_path}'

def create_all_presets():
    create_beat([5,1,4,1,5,1,4,1], '1.wav')
    create_beat([5,1,7,1,5,1,7,1], '2.wav')
    create_beat([3,1,6,1,3,1,6,1], '3.wav')
    create_beat([5,1,4,1,1,5,4,1], '4.wav')
    create_beat([5,1,4,1,5,5,4,1], '5.wav')
    create_beat([3,8,2,8,8,3,2,8], '6.wav')
    create_beat([4,1,4,5,1,5,5,4], '7.wav')
    create_beat([5,1,4,1,1,5,4,5], '8.wav')
    create_beat([4,5,5,1,5,5,1,4], '9.wav')

def get_preset_url(index):
    return s3_url_format.format(end_path='finished_beats/{}.wav'.format(index))

def get_hit_url(index):
    return s3_url_format.format(end_path='beat_creator/{}.wav'.format(index))

def get_AudioSegment_from_s3(index):
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
    file_name = '{}.wav'.format(index)
    key.key = 'beat_creator/{file_name}'.format(file_name=file_name)
    key.get_contents_to_filename(file_name)
    return AudioSegment.from_wav(file_name)


def send_beat_to_s3(filename):
    key = Key(bucket)
    s3_name = 'finished_beats/{filename}'.format(filename=filename)
    key.key = s3_name
    key.set_acl('public-read')
    key.set_contents_from_filename(filename)
    return s3_url_format.format(end_path=s3_name)


def create_beat(indices, file_name=None):
    samples = [None]*9
    indices = [int(n) for n in indices]
    unique_indices = set(indices)
    for i in unique_indices:
        if int(i) < 1 or int(i) > 8:
            raise Exception("Don't pass me that shit, bro.")
        samples[int(i)] = get_AudioSegment_from_s3(i)
    beat = (samples[indices[0]] + samples[indices[1]] + samples[indices[2]] + samples[indices[3]] + samples[indices[4]] + 
            samples[indices[5]] + samples[indices[6]] + samples[indices[7]])
    if not file_name:
        file_name = (str(indices[0]) + str(indices[1]) + str(indices[2]) + str(indices[3]) + str(indices[4]) + 
            str(indices[5]) + str(indices[6]) + str(indices[7]) + '.wav') 
    beat.export(file_name, format="wav")
    return send_beat_to_s3(file_name)
