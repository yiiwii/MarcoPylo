# altered into class
# this is a file support user recorded marco and pylo shout outs
# need to run as super user if in mac os
# from:https://www.thepythoncode.com/article/play-and-record-audio-sound-in-python
import pyaudio
import wave
import sounddevice as sd # used to check what device are used

class Recording():

    def __init__(self, name):
        self.name = name
        self.filename = f"{self.name}.wav"
        self.recording = None
        self.chunk = 1024
        self.FORMAT = pyaudio.paInt16
        self.channels = 2
        self.sample_rate = 44100
        self.record_seconds = 2
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.recordSave(2)
        self.saveAudio()
        
    def recordSave(self,index):
        print(sd.query_devices())
        # the file name output you want to record into
        # initialize PyAudio object
        # open stream object as input & output
        stream = self.p.open(format=self.FORMAT,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        input_device_index=index,
                        output=True,
                        frames_per_buffer=self.chunk)
        print("Recording...")
        for i in range(int(self.sample_rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            # if you want to hear your voice while recording
            # stream.write(data)
            self.frames.append(data)
        print("Finished recording.")
        # stop and close stream
        stream.stop_stream()
        stream.close()
        # terminate pyaudio object
        self.p.terminate()

    def saveAudio(self):
        # save audio file
        # open the file in 'write bytes' mode
        wf = wave.open(self.filename, "wb")
        # set the channels
        wf.setnchannels(self.channels)
        # set the sample format
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        # set the sample rate
        wf.setframerate(self.sample_rate)
        # write the frames as bytes
        wf.writeframes(b"".join(self.frames))
        # close the file
        wf.close()

    def playAudio(self):
        # Open the sound file 
        wf = wave.open(self.filename, "wb")
        stream = self.p.open(format = self.FORMAT,
                channels = self.channels,
                rate = self.sample_rate,
                output = True)
        # Read data in chunks
        data = wf.readframes(self.chunk)

        # Play the sound by writing the audio data to the stream
        while data != '':
            stream.write(data)
            data = wf.readframes(self.chunk)

        # Close and terminate the stream
        stream.close()
        p.terminate()

