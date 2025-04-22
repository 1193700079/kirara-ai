import asyncio
import os

from im_whatsapp_adapter.adapter import WhatsAppAdapter, WhatsAppConfig

from kirara_ai.logger import get_logger
from kirara_ai.plugin_manager.plugin import Plugin
from kirara_ai.web.app import WebServer

logger = get_logger("WA-Adapter")


class WhatsAppAdapterPlugin(Plugin):
    web_server: WebServer
    
    def __init__(self):
        pass

    def on_load(self):
        self.im_registry.register(
            "WhatsApp",
            WhatsAppAdapter,
            WhatsAppConfig,
            "WhatsApp 机器人",
            "WhatsApp 官方机器人，支持私聊、群聊、 Markdown 格式消息。",
            """
WhatsApp 机器人,配置流程可参考 [WhatsApp 官方文档](https://core.WhatsApp.org/bots/tutorial) 和 [Kirara AI 文档](https://kirara-docs.app.lss233.com/guide/configuration/im.html)。
            """
        )
        # 添加当前文件夹下的 assets/WhatsApp.svg 文件夹到 web 服务器
        local_logo_path = os.path.join(os.path.dirname(__file__), "assets", "whatsapp.png")
        self.web_server.add_static_assets("/assets/icons/im/whatsapp.png", local_logo_path)

    def on_start(self):
        pass

    def on_stop(self):
        try:
            tasks = []
            loop = asyncio.get_event_loop()
            for key, adapter in self.im_manager.get_adapters().items():
                if isinstance(adapter, WhatsAppAdapter) and adapter.is_running:
                    tasks.append(self.im_manager.stop_adapter(key, loop))
            for key in list(self.im_manager.get_adapters().keys()):
                self.im_manager.delete_adapter(key)
            loop.run_until_complete(asyncio.gather(*tasks))
        except Exception as e:

            logger.error(f"Error stopping WhatsApp adapter: {e}")
        finally:
            self.im_registry.unregister("WhatsApp")
        logger.info("WhatsApp adapter stopped")
