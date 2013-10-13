# beat creation script

from pydub import AudioSegment

def create_beat(i,j,k,l,m,n,o,p):
    samples = []
    samples.append(AudioSegment.from_wav("hihat.wav"))
    samples.append(AudioSegment.from_wav("snare.wav"))
    samples.append(AudioSegment.from_wav("bass.wav"))
    samples.append(AudioSegment.from_wav("hihatsnare.wav"))
    samples.append(AudioSegment.from_wav("hihatbass.wav"))
    samples.append(AudioSegment.from_wav("snarebass.wav"))
    samples.append(AudioSegment.from_wav("basshihatsnare.wav"))
    samples.append(AudioSegment.from_wav("silence.wav"))
    beat = samples[i] + samples[j] + samples[k] + samples[l] + samples[m] + samples[n] + samples[o] + samples[p]
    name = str(i+1) + str(j+1) + str(k+1) + str(l+1) + str(m+1) + str(n+1) + str(o+1) + str(p+1)
    return beat.export(name + ".wav", format="wav")
