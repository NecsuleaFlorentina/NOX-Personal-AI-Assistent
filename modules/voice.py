import threading
import wave
import os
import tempfile
import numpy as np
import sounddevice as sd
import speech_recognition as sr


class VoiceRecorder:
    RATE = 16000
    CHANNELS = 1

    def __init__(self, on_result=None, on_error=None, on_status=None):
        self._on_result = on_result
        self._on_error = on_error
        self._on_status = on_status
        self._recording = False
        self._frames = []
        self._thread = None
        self._recognizer = sr.Recognizer()

    def start(self):
        if self._recording:
            return
        self._recording = True
        self._frames = []
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        if self._on_status:
            self._on_status("recording")

    def stop(self):
        if not self._recording:
            return
        self._recording = False
        if self._on_status:
            self._on_status("transcribing")
        threading.Thread(target=self._transcribe, daemon=True).start()

    def _record_loop(self):
        try:
            with sd.InputStream(samplerate=self.RATE, channels=self.CHANNELS,
                                dtype='int16') as stream:
                while self._recording:
                    data, _ = stream.read(1024)
                    self._frames.append(data.copy())
        except Exception as e:
            if self._on_error:
                self._on_error(str(e))

    def _transcribe(self):
        try:
            if not self._frames:
                if self._on_error:
                    self._on_error("Nu s-a înregistrat nimic.")
                return

            # Salveaza ca WAV temporar
            audio_data = np.concatenate(self._frames, axis=0).flatten()
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()

            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data.astype(np.int16).tobytes())

            # Transcrie cu Google Speech Recognition (gratuit, fara API key)
            with sr.AudioFile(tmp_path) as source:
                audio = self._recognizer.record(source)

            os.unlink(tmp_path)

            text = self._recognizer.recognize_google(audio, language="ro-RO")

            if text and self._on_result:
                self._on_result(text)

            if self._on_status:
                self._on_status("idle")

        except sr.UnknownValueError:
            if self._on_error:
                self._on_error("Nu am înțeles nimic. Încearcă din nou.")
            if self._on_status:
                self._on_status("idle")
        except sr.RequestError as e:
            if self._on_error:
                self._on_error(f"Eroare conexiune Google: {e}")
            if self._on_status:
                self._on_status("idle")
        except Exception as e:
            if self._on_error:
                self._on_error(str(e))
            if self._on_status:
                self._on_status("idle")