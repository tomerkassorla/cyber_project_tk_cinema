import pyaudio
import wave

DIRECTORY = "C:\\tomer_python\\work_project\\work\\last_work2\\"


class Audio:
    """This class is responsible for audio playback.
     This class writes to a sound card and reads chunks from the file."""

    def __init__(self, file_name, protocol_msg):
        self.file_name = file_name
        if len(file_name) != 0:
            self.f = wave.open(DIRECTORY + self.file_name + '.wav', "rb")  # open a wav format music
            self.p = pyaudio.PyAudio()  # instantiate PyAudio
            self.stream = self.p.open(format=self.p.get_format_from_width(self.f.getsampwidth()),
                                      channels=self.f.getnchannels(),
                                      rate=self.f.getframerate(),
                                      output=True)  # open stream
        else:
            list_of_constants = protocol_msg.split("#")
            self.p = pyaudio.PyAudio()  # instantiate PyAudio
            self.stream = self.p.open(format=self.p.get_format_from_width(int(list_of_constants[0])),
                                      channels=int(list_of_constants[1]),
                                      rate=int(list_of_constants[2]),
                                      output=True)  # open stream
        self.chunk = 3000

    def readframes(self):
        return self.f.readframes(self.chunk)  # read chunk from file

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def write(self, data):
        self.stream.write(data)  # writes to the sound card

    def get_constants(self):
        return str(self.f.getsampwidth()) + "#" + str(self.f.getnchannels()) + "#" + str(self.f.getframerate())
