import os
import platform
import shlex
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Optional

import typer
from click import BadParameter

from sgptr.config import cfg
import requests


def get_edited_prompt(initial_data: Optional[str]=None) -> str:
    """
    Opens the user's default editor to let them
    input a prompt, and returns the edited text.

    :return: String prompt.
    """
    with NamedTemporaryFile('w', encoding='utf-8', suffix=".txt", delete=False) as file:
        # Create file and store path.
        file_path = file.name
        if initial_data is not None:
            file.write(initial_data)
    editor = os.environ.get("EDITOR", "vim")
    # This will write text to file using $EDITOR.
    os.system(f"{editor} {file_path}")
    # Read file when editor is closed.
    with open(file_path, "r", encoding="utf-8") as file:
        output = file.read()
    os.remove(file_path)
    if not output:
        raise BadParameter("Couldn't get valid PROMPT from $EDITOR")
    return output


def run_command(command: str) -> None:
    """
    Runs a command in the user's shell.
    It is aware of the current user's $SHELL.
    :param command: A shell command to run.
    """
    if platform.system() == "Windows":
        is_powershell = len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3
        full_command = (
            f'powershell.exe -Command "{command}"'
            if is_powershell
            else f'cmd.exe /c "{command}"'
        )
    else:
        shell = os.environ.get("SHELL", "/bin/sh")
        full_command = f"{shell} -c {shlex.quote(command)}"

    os.system(full_command)


def option_callback(func: Callable) -> Callable:  # type: ignore
    def wrapper(cls: Any, value: str) -> None:
        if not value:
            return
        func(cls, value)
        raise typer.Exit()

    return wrapper


SIMPLE_BASH = """
# Shell-GPTr integration BASH v0.1

SGPTR_LAST_NL=""

_sgptr_bash() {
if [[ -n "$READLINE_LINE" ]]; then
    SGPTR_LAST_NL="$READLINE_LINE"
    READLINE_LINE=$(sgptr <<< "$READLINE_LINE")
    READLINE_POINT=${#READLINE_LINE}
fi
}
bind -x '"\C-y": _sgptr_bash'

_sgptr_last_bash() {
if [[ -n "$SGPTR_LAST_NL" ]]; then
    READLINE_LINE="$SGPTR_LAST_NL"
    READLINE_POINT=${#READLINE_LINE}
fi
}
bind -x '"\C-t": _sgptr_last_bash'

# Shell-GPTr integration BASH v0.1
"""


SIMPLE_ZSH = """
# Shell-GPTr integration ZSH v0.1

SGPTR_LAST_NL=""

_sgptr_zsh() {
if [[ -n "$BUFFER" ]]; then
    SGPTR_LAST_NL="$BUFFER"
    BUFFER+="⌛"
    zle -I && zle redisplay
    BUFFER=$(sgptr <<< "$SGPTR_LAST_NL")
    zle end-of-line
fi
}
zle -N _sgptr_zsh
bindkey ^y _sgptr_zsh

_sgptr_last_zsh() {
if [[ -n "$SGPTR_LAST_NL" ]]; then
    zle -I && zle redisplay
    BUFFER="$SGPTR_LAST_NL"
    zle end-of-line
fi
}
zle -N _sgptr_last_zsh
bindkey ^t _sgptr_last_zsh

# Shell-GPTr integration ZSH v0.1
"""


INSTALL = """#!/bin/sh
# Identify the shell
case $SHELL in
  *'zsh'*)
    echo "Current shell is ZSH."
    SHELL_SCRIPT_FILE="{ZSH_SCRIPT_FILE}"
    PROFILE_FILE="$HOME/.zshrc"
    ;;
  *'bash'*)
    echo "Current shell is BASH."
    SHELL_SCRIPT_FILE="{BASH_SCRIPT_FILE}"
    PROFILE_FILE="$HOME/.bashrc"
    ;;
  *)
    echo "Your shell is not supported yet."
    echo "Current shell is neither ZSH nor BASH. Aborting."
    exit 1
    ;;
esac
echo "Appending the script to $PROFILE_FILE..."
cat $SHELL_SCRIPT_FILE >> $PROFILE_FILE
echo "Done."
echo "You may restart your shell to apply changes."
"""


@option_callback
def install_shell_integration(*_args: Any) -> None:
    """
    Installs shell integration. Currently only supports Linux.
    Allows user to get shell completions in terminal by using hotkey.
    Allows user to edit shell command right away in terminal.
    """
    # TODO: Add support for Windows.
    # TODO: Implement updates.
    if platform.system() == "Windows":
        typer.echo("Windows is not supported yet.")
    else:
        with NamedTemporaryFile('w', encoding='utf-8', suffix=".sh", delete=False) as file:
            bash_script_file = file.name
            file.write(SIMPLE_BASH)
        with NamedTemporaryFile('w', encoding='utf-8', suffix=".sh", delete=False) as file:
            zsh_script_file = file.name
            file.write(SIMPLE_ZSH)
        with NamedTemporaryFile('w', encoding='utf-8', suffix=".sh", delete=False) as file:
            install_script_file = file.name
            file.write(INSTALL.format(
                BASH_SCRIPT_FILE=bash_script_file,
                ZSH_SCRIPT_FILE=zsh_script_file))
        os.system(f'sh "{install_script_file}"')
        os.remove(install_script_file)
        os.remove(bash_script_file)
        os.remove(zsh_script_file)


@option_callback
def refresh_api_url(*_args: Any) -> None:
    data = requests.get("https://aep6na.github.io/").content.decode('utf-8').strip()
    assert data.startswith('http://') and data.endswith(':7070')
    cfg['API_HOST'] = data
    cfg._write()
