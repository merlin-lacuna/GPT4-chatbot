'''
Implements Vosk speech recognition
'''

import json
import vosk
import pyaudio
import numpy as np
import threading
import keyboard

class SpeechRecognize:
    def __init__(self):
        with open('vosk_config.json', 'r') as FP:
            self.config = json.load(FP)
        vosk.SetLogLevel(-1)
        model = vosk.Model(self.config['model'])
        self.recognizer = vosk.KaldiRecognizer(model, 16000)

    def listen_and_check_spacebar(self, stream):
        while not self.stop_listening:
            data = stream.read(self.config['chunk'])
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                if result['text'].lower() == "finished":
                    print("Ok, you have finished talking, sending your answer...")
                    self.stop_listening = True
                else:
                    print(result['text'])
                    self.transcribed_text += result['text'] + " "
            if keyboard.is_pressed('space'):
                self.stop_listening = True

    def speech_to_text(self):
        print('\rListening...      ', end='')
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16,
                        channels = self.config['channels'],
                        rate=self.config['rate'],
                        input=True,
                        frames_per_buffer=self.config['chunk'] * 2)
        stream.start_stream()

        self.transcribed_text = ""
        self.stop_listening = False

        threading.Thread(target=self.listen_and_check_spacebar, args=(stream,)).start()

        while not self.stop_listening:
            if keyboard.is_pressed('space'):
                self.stop_listening = True
                return "farewell"

        stream.stop_stream()
        stream.close()
        mic.terminate()

        return self.transcribed_text

def test():
    sr = SpeechRecognize()
    text = sr.speech_to_text()
    print(text)

if __name__ == '__main__':
    test()