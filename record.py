import pyaudio
import wave


def start_record(self, wFile, time, state):

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = time
    WAVE_OUTPUT_FILENAME = wFile
 
    audio = pyaudio.PyAudio()
 
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    if time == 3 :
        self.state = "Say Yes or No, \nRecording...."
        print "SAY YES OR NO"
    else:
        print "recording..."
        self.state = "Recording...."
    self.repaint()
    frames = []
 
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"
    self.state = "Finished Record"
    self.repaint()
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
 
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

if __name__ == '__main__':
    start_record("Commands/Happy.wav",6)