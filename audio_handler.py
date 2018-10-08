
#!/usr/bin/python
# -*- coding: utf-8 -*-

import wave
import pyaudio
import time
import threading
import logging
from ctypes import CFUNCTYPE, c_char_p, c_int,cdll
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

def play_audio_file(fname=None):
    """Simple callback function to play a wave file.
    :param str fname: wave file name
    :return: None
    """
    if not fname:
        logger.error("No audio file to play")
        return
    logger.debug("Playing '{}' file".format(fname))
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with no_alsa_error():
        audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

def play_async_audio_file(fname=None):
    """Simple function to play a wave file asynchronoulsy.
    :param str fname: wave file name
    :return: None
    """
    if not fname:
        logger.error("No audio file to play")
        return

    threading.Thread(target=play_audio_file, args=[fname]).start()
