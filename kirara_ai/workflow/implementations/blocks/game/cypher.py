import random
import re
from typing import Any, Dict

from kirara_ai.im.message import IMMessage, TextMessage
from kirara_ai.im.sender import ChatSender
from kirara_ai.workflow.core.block import Block
from kirara_ai.workflow.core.block.input_output import Input, Output


class Cypher(Block):
    """骰子掷点 block"""

    name = "dice_roll"
    inputs = {
        "message": Input("message", "输入消息", IMMessage, "用户的任意输入")
    }
    outputs = {
        "response": Output(
            "response", "响应消息", IMMessage, "响应消息-指定回复"
        )
    }

    def execute(self, message: IMMessage) -> Dict[str, Any]:
        # 解析命令
        command = message.content
        return {
            "response": IMMessage(
                sender=ChatSender.get_bot_sender(), 
                message_elements=[TextMessage(command + "-- 固定回复 -- 您好，我是cypher的测试block插件 !")]
            )
        }
