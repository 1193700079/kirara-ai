# coding=utf-8
#
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio

#  
#  python3 -m pip install --upgrade pip setuptools wheel
# sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
#  apt install portaudio19-dev
#  apt install  python3-pyaudio
#  pip install pyaudio
# ImportError: /root/anaconda3/lib/libstdc++.so.6: version `GLIBCXX_3.4.32' not found (required by /lib/x86_64-linux-gnu/libjack.so.0)
#  add-apt-repository ppa:ubuntu-toolchain-r/test
#  apt-get update
#  apt-get install --only-upgrade libstdc++6
# cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6   /root/anaconda3/lib/
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import time
import pyaudio
import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts_v2 import *

from datetime import datetime

dashscope.api_key = "sk-9ac9d24afd134378bae29adbb11ef81d"

model = "cosyvoice-v2"
voice = "longxiaoxia_v2"

def get_timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("[%Y-%m-%d %H:%M:%S.%f]")
    return formatted_timestamp

# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
# dashscope.api_key = "your-api-key"

model = "cosyvoice-v1"
voice = "longxiaochun"


class Callback(ResultCallback):
    _player = None
    _stream = None

    def on_open(self):
        print("websocket is open.")
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=22050, output=True
        )

    def on_complete(self):
        print(get_timestamp() + " speech synthesis task complete successfully.")

    def on_error(self, message: str):
        print(f"speech synthesis task failed, {message}")

    def on_close(self):
        print(get_timestamp() + " websocket is closed.")
        # 停止播放器
        self._stream.stop_stream()
        self._stream.close()
        self._player.terminate()

    def on_event(self, message):
        pass

    def on_data(self, data: bytes) -> None:
        print(get_timestamp() + " audio result length: " + str(len(data)))
        self._stream.write(data)


callback = Callback()

test_text = [
    "流式文本语音合成SDK，",
    "可以将输入的文本",
    "合成为语音二进制数据，",
    "相比于非流式语音合成，",
    "流式合成的优势在于实时性",
    "更强。用户在输入文本的同时",
    "可以听到接近同步的语音输出，",
    "极大地提升了交互体验，",
    "减少了用户等待时间。",
    "适用于调用大规模",
    "语言模型（LLM），以",
    "流式输入文本的方式",
    "进行语音合成的场景。",
]

synthesizer = SpeechSynthesizer(
    model=model,
    voice=voice,
    format=AudioFormat.PCM_22050HZ_MONO_16BIT,  
    callback=callback,
)


for text in test_text:
    synthesizer.streaming_call(text)
    time.sleep(0.1)
synthesizer.streaming_complete()

print('[Metric] requestId: {}, first package delay ms: {}'.format(
    synthesizer.get_last_request_id(),
    synthesizer.get_first_package_delay()))