import base64
from typing import Any, Dict, Optional
import dashscope
from dashscope.audio.tts_v2 import *

import requests

from kirara_ai.im.message import ImageMessage
from kirara_ai.workflow.core.block import Block
from kirara_ai.workflow.core.block.input_output import Input, Output
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
from abc import ABC, abstractmethod

from kirara_ai.im.message import ImageMessage, IMMessage, MessageElement, TextMessage,VoiceMessage
from kirara_ai.im.sender import ChatSender
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.llm.format import LLMChatMessage, LLMChatTextContent
from kirara_ai.llm.format.message import LLMChatContentPartType, LLMChatImageContent
from kirara_ai.llm.format.request import LLMChatRequest
from kirara_ai.llm.format.response import LLMChatResponse
from kirara_ai.llm.llm_manager import LLMManager
from kirara_ai.llm.llm_registry import LLMAbility
from kirara_ai.logger import get_logger
from kirara_ai.memory.composes.base import ComposableMessageType
from kirara_ai.workflow.core.block import Block, Input, Output, ParamMeta
from kirara_ai.workflow.core.execution.executor import WorkflowExecutor
from kirara_ai.ioc.container import DependencyContainer

dashscope.api_key = "sk-9ac9d24afd134378bae29adbb11ef81d"

class TTSCypherBlock(Block):
    name = "simple_tts"
    inputs = {
        "text": Input(
            name="text",
            label="含URL的文本",
            data_type=str,
            description="用户输入的文本内容"
        ),
        "voice": Input(
            name="voice",
            label="输入音色",
            data_type=str,
            description="指定一个音色,默认为longxiaoxia_v2,详情请查看 : https://help.aliyun.com/zh/model-studio/cosyvoice-python-api?spm=a2c4g.11186623.help-menu-2400256.d_2_4_0_1.5442244044t8WM",
            default=None
        )
    }
    outputs = {"msg": Output("msg", "IM消息", IMMessage, "IM消息")}

    def __init__(
        self,    ):
        self.logger = get_logger("TTSCythonBlock")

    def execute(self, text: str,voice: str =None) -> Dict[str, Any]:
        message_elements = []
        model = "cosyvoice-v2"
        if not voice:
            voice = "longxiaoxia_v2"
        synthesizer = SpeechSynthesizer(model=model, voice=voice)
        audio = synthesizer.call(text)
        self.logger.info('[Metric] requestId: {}, first package delay ms: {}'.format(
            synthesizer.get_last_request_id(),
            synthesizer.get_first_package_delay()))
        message_elements.append(VoiceMessage(data = audio))
        return {"msg": IMMessage(sender=ChatSender.get_bot_sender(), message_elements=message_elements)}