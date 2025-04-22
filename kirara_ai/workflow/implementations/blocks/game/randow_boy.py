import random
import re
import aiohttp
import asyncio
from typing import Any, Dict

from kirara_ai.im.message import IMMessage, TextMessage
from kirara_ai.im.sender import ChatSender
from kirara_ai.workflow.core.block import Block
from kirara_ai.workflow.core.block.input_output import Input, Output

import asyncio
from kirara_ai.logger import get_logger
from kirara_ai.ioc.container import DependencyContainer

logger = get_logger("RandomBoy")

class RandomBoy(Block):

    name = "random_boy_video"
    description = "随机获取1个视频，可重复调用获取多个"

    # inputs = {}  # 不需要输入参数
    inputs = {
        "message": Input("message", "输入消息", IMMessage, "用户的任意输入")
    }
    outputs = {
        "video_url": Output(name="video_url", label="视频链接", data_type=str, description="视频直链地址")
    }

    async def get_random_video(self) -> str:
        """获取随机美女视频链接"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.317ak.com/API/sp/sgxl.php",
                    # "https://api.lolimi.cn/API/xjj/xjj.php",
                    allow_redirects=False  # 不自动跟随重定向
                ) as response:
                    print(response)
                    logger.info("")
                    if response.status == 302:  # 检查是否有重定向
                        redirect_url = response.headers.get('Location')
                        if not redirect_url.endswith(".jpg"):
                            return 'https://api.317ak.com/API/sp/' + redirect_url
                # async with session.get(
                #     "https://api.lolimi.cn/API/sjsp/api.php",
                #     allow_redirects=False  # 不自动跟随重定向
                # ) as response:
                #     result = await response.json()
                #     if "data" in result and "url" in result["data"]:
                #         return result["data"]["url"]
                #     else:
                #         raise Exception(f"请求失败，状态码: {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"获取视频链接失败: {str(e)}")

    def execute(self,message: IMMessage) -> Dict[str, Any]:
        
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            video_url = loop.run_until_complete(
                self.get_random_video()
            )
            logger.info(f"video_url,视频链接: {str(video_url)}")
            # 格式化输出字符串
            return {"video_url": video_url}
        except Exception as e:
            return {"video_url": f"获取视频失败: {str(e)}"}
