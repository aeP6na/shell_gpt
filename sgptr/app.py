"""
This module provides a simple interface for OpenAI API using Typer
as the command line interface. It supports different modes of output including
shell commands and code, and allows users to specify the desired OpenAI model
and length and other options of the output. Additionally, it supports executing
shell commands directly from the interface.
"""
# To allow users to use arrow keys in the REPL.
import readline  # noqa: F401
import sys

import typer
from click import MissingParameter
from click.types import Choice

from sgptr.config import cfg
from sgptr.handler import Handler
from sgptr.utils import (
    get_edited_prompt,
    run_command,
)


def main(
    prompt: str = typer.Argument(
        None,
        show_default=False,
        help="The prompt to generate completions for.",
    ),
    temperature: float = typer.Option(
        0.1,
        min=0.0,
        max=2.0,
        help="Randomness of generated output.",
    ),
    top_probability: float = typer.Option(
        1.0,
        min=0.1,
        max=1.0,
        help="Limits highest probable tokens (words).",
    ),
    cache: bool = typer.Option(
        True,
        help="Cache completion results.",
    ),
) -> None:
    stdin_passed = not sys.stdin.isatty()

    if stdin_passed:
        prompt = f"{sys.stdin.read()}\n\n{prompt or ''}"

    if not prompt:
        raise MissingParameter(param_hint="PROMPT", param_type="string")

    data = dict(
        prompt=prompt,
        temperature=temperature,
        top_probability=top_probability,
        caching=cache,
    )

    full_completion = Handler().handle(**data)

    data['response'] = full_completion
    data['option'] = []

    while not stdin_passed:
        option = typer.prompt(
            text="[E]xecute, [M]odify, [A]bort",
            type=Choice(("e", "m", "a"), case_sensitive=False),
            default="e" if cfg.get("DEFAULT_EXECUTE_SHELL_CMD") == "true" else "a",
            show_choices=False,
            show_default=False,
        )
        data['option'].append(option)
        if option == "e":
            run_command(full_completion)
        elif option == "m":
            full_completion = get_edited_prompt(full_completion).strip()
            data['option'].append(full_completion)
            typer.secho(full_completion, fg=cfg.get("DEFAULT_COLOR"), bold=True)
            continue
        break
    
    Handler().upload(data)


def entry_point() -> None:
    # Python package entry point defined in setup.py
    typer.run(main)


if __name__ == "__main__":
    entry_point()
