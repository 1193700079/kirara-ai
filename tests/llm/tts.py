# coding=utf-8

import dashscope
from dashscope.audio.tts_v2 import *

# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
dashscope.api_key = "sk-9ac9d24afd134378bae29adbb11ef81d"

model = "cosyvoice-v2"
voice = "longxiaoxia_v2"

synthesizer = SpeechSynthesizer(model=model, voice=voice)
audio = synthesizer.call("今天天气怎么样？")
print('[Metric] requestId: {}, first package delay ms: {}'.format(
    synthesizer.get_last_request_id(),
    synthesizer.get_first_package_delay()))

with open('output.mp3', 'wb') as f:
    f.write(audio)