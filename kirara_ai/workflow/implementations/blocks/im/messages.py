import re
import asyncio
import requests

from typing import Annotated, Any, Dict, List, Optional
from urllib.parse import urlparse, unquote

from kirara_ai.logger import get_logger
from kirara_ai.im.adapter import IMAdapter
from kirara_ai.im.manager import IMManager
from kirara_ai.im.message import IMMessage, MessageElement, TextMessage, ImageMessage, VoiceMessage,VideoElement
from kirara_ai.im.sender import ChatSender
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.workflow.core.block import Block, Input, Output, ParamMeta


def im_adapter_options_provider(container: DependencyContainer, block: Block) -> List[str]:
    return [key for key, _ in container.resolve(IMManager).adapters.items()]

class GetIMMessage(Block):
    """获取 IM 消息"""

    name = "msg_input"
    container: DependencyContainer
    outputs = {
        "msg": Output("msg", "IM 消息", IMMessage, "获取 IM 发送的最新一条的消息"),
        "sender": Output("sender", "发送者", ChatSender, "获取 IM 消息的发送者"),
    }

    def execute(self, **kwargs) -> Dict[str, Any]:
        msg = self.container.resolve(IMMessage)
        return {"msg": msg, "sender": msg.sender}


class SendIMMessage(Block):
    """发送 IM 消息"""

    name = "msg_sender"
    inputs = {
        "msg": Input("msg", "IM 消息", IMMessage, "要从 IM 发送的消息"),
        "target": Input(
            "target",
            "发送对象",
            ChatSender,
            "要发送给谁，如果填空则默认发送给消息的发送者",
            nullable=True,
        ),
    }
    outputs = {}
    container: DependencyContainer

    def __init__(
        self, im_name: Annotated[Optional[str], ParamMeta(label="聊天平台适配器名称", options_provider=im_adapter_options_provider)] = None
    ):
        self.im_name = im_name

    def execute(
        self, msg: IMMessage, target: Optional[ChatSender] = None
    ) -> Dict[str, Any]:
        src_msg = self.container.resolve(IMMessage)
        if not self.im_name:
            adapter = self.container.resolve(IMAdapter)
        else:
            adapter = self.container.resolve(
                IMManager).get_adapter(self.im_name)
        loop: asyncio.AbstractEventLoop = self.container.resolve(
            asyncio.AbstractEventLoop
        )
        loop.create_task(adapter.send_message(msg, target or src_msg.sender))
        return {"ok": True}

# IMMessage 转纯文本


class IMMessageToText(Block):
    """IMMessage 转纯文本"""

    name = "im_message_to_text"
    container: DependencyContainer
    inputs = {"msg": Input("msg", "IM 消息", IMMessage, "IM 消息")}
    outputs = {"text": Output("text", "纯文本", str, "纯文本")}

    def execute(self, msg: IMMessage) -> Dict[str, Any]:
        return {"text": msg.content}


# 纯文本转 IMMessage
class TextToIMMessage(Block):
    """纯文本转 IMMessage"""

    name = "text_to_im_message"
    container: DependencyContainer
    inputs = {"text": Input("text", "纯文本", str, "纯文本")}
    outputs = {"msg": Output("msg", "IM 消息", IMMessage, "IM 消息")}

    def __init__(self, split_by: Annotated[Optional[str], ParamMeta(label="分段符")] = None):
        self.split_by = split_by

    def execute(self, text: str) -> Dict[str, Any]:
        if self.split_by:
            return {"msg": IMMessage(sender=ChatSender.get_bot_sender(), message_elements = [TextMessage(line.strip()) for line in text.split(self.split_by) if line.strip()])}
        else:
            return {"msg": IMMessage(sender=ChatSender.get_bot_sender(), message_elements=[TextMessage(text)])}

# 补充 IMMessage 消息
class AppendIMMessage(Block):
    """补充 IMMessage 消息"""

    name = "concat_im_message"
    container: DependencyContainer
    inputs = {
        "base_msg": Input("base_msg", "IM 消息", IMMessage, "IM 消息"),
        "append_msg": Input("append_msg", "新消息片段", MessageElement, "新消息片段"),
    }
    outputs = {"msg": Output("msg", "IM 消息", IMMessage, "IM 消息")}

    def execute(self, base_msg: IMMessage, append_msg: MessageElement) -> Dict[str, Any]:
        return {"msg": IMMessage(sender=base_msg.sender, message_elements=base_msg.message_elements + [append_msg])}


class URLToMessageCypherBlock(Block):
    """URL转换Block"""
    name = "url_to_message_cypher"
    description = "将结果中的URL转换为IMMessage"
    container: DependencyContainer
    inputs = {
        "text": Input(
            name="text",
            label="含URL的文本",
            data_type=str,
            description="包含URL的文本内容"
        )
    }
    outputs = {
        "message": Output(
            name="message",
            label="消息对象",
            data_type=IMMessage,
            description="转换后的消息对象"
        )
    }

    def __init__(self):
        self.logger = get_logger("URLToMessageBlock")

    def coverAndSendMessage(self, message: str) -> IMMessage:
        # 首先替换掉转义的换行符为实际换行符
        message = message.replace('\\n', '\n')
        # 修改正则表达式以正确处理换行符分隔的URL
        url_pattern = r'https?://[^\s\n<>\"\']+|www\.[^\s\n<>\"\']+'
        # 文件扩展名列表
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.tiff'}
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.midi', '.mid'}
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'}

        try:
            urls = re.findall(url_pattern, message)
            print(urls)
            # If no URLs found, return text message
            if not urls:
                return None
            message_elements = []
            for url in urls:
                try:
                    # Parse URL
                    parsed = urlparse(url)
                    path = unquote(parsed.path)

                    # Get extension from path
                    ext = None
                    if '.' in path:
                        ext = '.' + path.split('.')[-1].lower()
                        if '/' in ext or len(ext) > 10:
                            ext = None

                    # 使用URL直接创建消息对象，而不是下载内容
                    if any(x in url for x in image_extensions):
                        message_elements.append(ImageMessage(url=url))
                        continue
                    elif any(x in url for x in audio_extensions):
                        message_elements.append(VoiceMessage(url=url))
                        continue
                    elif any(x in url for x in video_extensions):
                        message_elements.append(VideoElement(url=url))
                        continue
                    try:
                        response = requests.head(url, allow_redirects=True, timeout=5)
                        content_type = response.headers.get('Content-Type', '').lower()
                    except Exception as e:
                        self.logger.warning(f"Failed to get headers for {url}: {str(e)}")
                        content_type = ''
                    self.logger.debug(content_type)
                    # Check content type first, then fall back to extension
                    if any(x in content_type for x in ['image', 'png', 'jpg', 'jpeg', 'gif']):
                        message_elements.append(ImageMessage(url=url))
                    elif any(x in content_type for x in ['video', 'mp4', 'avi', 'mov']):
                        message_elements.append(VideoElement(url=url))
                    elif any(x in content_type for x in ['audio', 'voice', 'mp3', 'wav']):
                        message_elements.append(VoiceMessage(url=url))
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                    continue
            # If we got here, we found URLs but couldn't process them
            if message_elements:
                return IMMessage(
                    sender="bot",
                    raw_message=message,
                    message_elements=message_elements
                )
        except Exception as e:
            self.logger.error(f"Error in coverAndSendMessage: {str(e)}")
        return None
    
    def execute(self, text: str) -> Dict[str, Any]:
        try:
            # Direct call to coverAndSendMessage
            message = self.coverAndSendMessage(text)
            return {"message": message}
        except Exception as e:
            self.logger.error(f"Error converting URL to message: {str(e)}")
            return {
                "message": IMMessage(
                    sender="bot",
                    raw_message=text,
                    message_elements=[TextMessage("")]
                )
            }


class DifyToMessageCypherBlock(Block):
    """URL转换Block"""
    name = "dify_to_message_cypher"
    description = "将dify输出的内容转换为IMMessage"
    container: DependencyContainer
    inputs = {
        "text": Input(
            name="text",
            label="用户发送的消息",
            data_type=str,
            description="用户从IM中发送的消息"
        )
    }
    outputs = {
        "message": Output(
            name="message",
            label="消息对象",
            data_type=IMMessage,
            description="转换后的消息对象"
        )
    }

    def __init__(self):
        self.logger = get_logger("DifyToMessageCypherBlock")

    def dify_ask(self,text):
        import requests
        url = "http://47.236.152.135/v1/chat-messages"
        api_key = "app-QgzAtwP6ukQWmwpBAzew12j6"  # 替换为实际的 API 密钥
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": {},
            "query": text,
            "conversation_id": "",
            "user": "abc-123",
            # "files": [
            #     {
            #         "type": "image",
            #         "transfer_method": "remote_url",
            #         "url": "https://cloud.dify.ai/logo/logo-site.png"
            #     }
            # ]
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            data = response.json()
            if response.status_code == 200:
                self.logger.info("dify 请求成功！")
                self.logger.info(f"响应全部内容: {response.json()}" )  
                self.logger.info(f"响应文本内容: {data['answer']}" ) 
                self.logger.info(f"响应usage内容: {data['metadata']['usage']}" ) 
                return data['answer']
            else:
                self.logger.error(f"请求失败，状态码: {response.status_code}")
                self.logger.error(f"错误信息:  {response.text}") 
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求过程中发生异常: {str(e)}")
            return None
         
    def execute(self, text: str) -> Dict[str, Any]:
        try:
            dify_ans = self.dify_ask(text)
            return {
                "message": IMMessage(
                    sender="bot",
                    raw_message=text,
                    message_elements=[TextMessage(dify_ans)]
                )
            }
        
        except Exception as e:
            self.logger.error(f"Error converting URL to message: {str(e)}")
            return {
                "message": IMMessage(
                    sender="bot",
                    raw_message=text,
                    message_elements=[TextMessage("")]
                )
            }