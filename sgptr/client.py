import json
from pathlib import Path
from typing import Generator

import requests

from .cache import Cache
from .config import cfg
from .role import SystemRole

CACHE_LENGTH = int(cfg.get("CACHE_LENGTH"))
CACHE_PATH = Path(cfg.get("CACHE_PATH"))
REQUEST_TIMEOUT = int(cfg.get("REQUEST_TIMEOUT"))


class SGPTRClient:
    cache = Cache(CACHE_LENGTH, CACHE_PATH)

    def __init__(self, api_host: str) -> None:
        self.api_host = api_host

    @cache
    def _request(
        self,
        prompt: str,
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        """
        Make request to OpenAI API, read more:
        https://platform.openai.com/docs/api-reference/chat

        :param messages: List of messages {"role": user or assistant, "content": message_string}
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301
        :param temperature: Float in 0.0 - 2.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :return: Response body JSON.
        """
        vars = SystemRole.get_variables()
        data = {
            'shell': vars['shell'],
            'os': vars['os'],
            'prompt': prompt,
            'temperature': temperature,
            'top_probability': top_probability,
        }
        endpoint = f"{self.api_host}/generate/stream"
        response = requests.post(
            endpoint,
            # Hide API key from Rich traceback.
            headers={
                "Content-Type": "application/json",
            },
            json=data,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()
        # TODO: Optimise.
        # https://github.com/openai/openai-python/blob/237448dc072a2c062698da3f9f512fae38300c1c/openai/api_requestor.py#L98
        for line in response.iter_lines():
            data = line.lstrip(b"data: ").decode("utf-8")
            # if data == "[DONE]":  # type: ignore
            #     break
            if not data:
                continue
            data = json.loads(data)  # type: ignore
            yield data

    def get_completion(
        self,
        prompt: str,
        temperature: float = 1,
        top_probability: float = 1,
        caching: bool = True,
    ) -> Generator[str, None, None]:
        """
        Generates single completion for prompt (message).

        :param messages: List of dict with messages and roles.
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301.
        :param temperature: Float in 0.0 - 1.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :param caching: Boolean value to enable/disable caching.
        :return: String generated completion.
        """
        yield from self._request(
            prompt,
            temperature,
            top_probability,
            caching=caching,
        )

    def upload(self, data):
        endpoint = f"{self.api_host}/upload"
        requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=REQUEST_TIMEOUT,
        )
