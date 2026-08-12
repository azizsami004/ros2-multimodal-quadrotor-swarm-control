import json
import queue
import sys
import threading
from pathlib import Path

import sounddevice as sd

from ament_index_python.packages import get_package_share_directory
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from vosk import KaldiRecognizer, Model

class VoiceController(QObject):
    command_recognized = pyqtSignal(str)
    text_recognized = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    VALID_COMMANDS = ('forward', 'backward', 'left', 'right', 'up', 'down', 'stop')

    def __init__(self):
        super().__init__()

        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

    def audio_callback(self, indata, frames, time_information, status):

        if status:
            print(status, file=sys.stderr)

        if not self.stop_event.is_set():
            self.audio_queue.put(bytes(indata))

    def extract_command(self, recognized_text):
        words = recognized_text.lower().split()

        for command in self.VALID_COMMANDS:
            if command in words:
                return command

        return None

    def get_model_path(self):
        package_share = Path(get_package_share_directory('task1_quadrotor'))

        model_path = (
            package_share
            / 'models'
            / 'vosk-model-small-en-us-0.15'
        )

        return model_path

    def clear_audio_queue(self):
        while True:
            try: 
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    @pyqtSlot()
    def start_listening(self):
        self.stop_event.clear()
        self.clear_audio_queue()

        try:
            model_path = self.get_model_path()

            if not model_path.exists():
                raise FileNotFoundError(
                    f'Vosk model was not found at: '
                    f'{model_path}'
                )

            self.status_changed.emit(
                'Loading voice model...'
            )

            model = Model(str(model_path))

            microphone_information = sd.query_devices(
                device=None,
                kind='input'
            )

            sample_rate = int(
                microphone_information[
                    'default_samplerate'
                ]
            )

            recognizer = KaldiRecognizer(
                model,
                sample_rate
            )

            self.status_changed.emit(
                f"Listening using "
                f"{microphone_information['name']}"
            )

            with sd.RawInputStream(
                samplerate=sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            ):
                while not self.stop_event.is_set():

                    try:
                        audio_data = self.audio_queue.get(
                            timeout=0.1
                        )

                    except queue.Empty:
                        continue

                    complete_phrase = (
                        recognizer.AcceptWaveform(
                            audio_data
                        )
                    )

                    if not complete_phrase:
                        continue

                    result = json.loads(
                        recognizer.Result()
                    )

                    recognized_text = result.get(
                        'text',
                        ''
                    ).strip()

                    if not recognized_text:
                        continue

                    self.text_recognized.emit(
                        recognized_text
                    )

                    command = self.extract_command(
                        recognized_text
                    )

                    if command is not None:
                        self.command_recognized.emit(
                            command
                        )

        except sd.PortAudioError as error:
            self.error_occurred.emit(
                f'Microphone error: {error}'
            )

        except Exception as error:
            self.error_occurred.emit(
                f'{type(error).__name__}: {error}'
            )

        finally:
            self.status_changed.emit(
                'Microphone off'
            )

            self.clear_audio_queue()
            self.finished.emit()

    def stop_listening(self):
        self.stop_event.set()


