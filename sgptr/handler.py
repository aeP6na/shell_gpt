from typing import Any, Generator

import typer

from .client import SGPTRClient
from .config import cfg


class Handler:
    def __init__(self) -> None:
        self.client = SGPTRClient(cfg.get("API_HOST"))
        self.color = cfg.get("DEFAULT_COLOR")

    def get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        yield from self.client.get_completion(**kwargs)

    def handle(self, prompt: str, **kwargs: Any) -> str:
        full_completion = ""
        for word in self.get_completion(prompt=prompt, **kwargs):
            typer.secho(word, fg=self.color, bold=True, nl=False)
            full_completion += word
        typer.echo()
        return full_completion

    def upload(self, data):
        self.client.upload(data)
