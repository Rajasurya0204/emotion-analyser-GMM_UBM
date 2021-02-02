import pyaudio
import wave


def start_play(file_play, choice=1):
    # define stream chunk
    chunk = 1024

    # open a wav format music
    if choice == 1:
        f = wave.open("Commands/"+file_play, "rb")
    else:
        f = wave.open("Test/"+file_play, "rb")
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()), channels=f.getnchannels(), rate=f.getframerate(), output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()
