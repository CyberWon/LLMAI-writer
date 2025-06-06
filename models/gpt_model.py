import aiohttp
import json
import asyncio
from models.ai_model import AIModel

class GPTModel(AIModel):
    """OpenAI GPT模型实现"""

    def __init__(self, config_manager):
        """
        初始化GPT模型

        Args:
            config_manager: 配置管理器实例
        """
        super().__init__(config_manager)
        self.api_key = config_manager.get_api_key('gpt')
        self.model_name = config_manager.get_model_name('gpt')
        self.api_url = "https://api.openai.com/v1/chat/completions"

        if not self.api_key:
            raise ValueError("OpenAI API密钥未配置")

        if not self.model_name:
            self.model_name = "gpt-4-turbo"

    async def generate(self, prompt, callback=None):
        """
        生成文本（非流式）

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=data,
                proxy=self.proxy["https"] if self.proxy else None
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt, callback=None):
        """
        流式生成文本

        Args:
            prompt: 提示词
            callback: 回调函数，用于处理生成的文本块

        Returns:
            生成的文本流（异步生成器）
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=data,
                proxy=self.proxy["https"] if self.proxy else None
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        json_str = line[6:]
                        try:
                            data = json.loads(json_str)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
