# ShellGPT for Research (sgptr)

*Use ShellGPT WITHOUT an OpenAI API key. It is totally free!*

This is a research project. We want to collect data on programmers' real world use cases of Shell commands. We discovered this excellent project [ShellGPT (sgpt)](https://github.com/TheR1D/shell_gpt), forked it, and made some modifications. Now, you can use it for **free**.

**WARNING: Although sgptr is free to use, it will upload your prompt and feedback to our server. So DO NOT put anything sensitive (e.g. password) when you are using sgptr.**

What data will we collect?
- Prompt: Your prompt is sent to our server.
- Feedback: After sgptr responds, you can choose to Execute, Modify or Abort. Your choice will be uploaded to our server. If you choose to Modify, your modified command will also be uploaded. Note the execution result or status will NOT be collected.

However, sgptr is not as powerful as sgpt, because we have truncated many functions unrelated to Shell commands. The following parts are the introductions from the original repo.

A command-line productivity tool powered by OpenAI's GPT models. As developers, we can leverage AI capabilities to generate shell commands, code snippets, comments, and documentation, among other things. Forget about cheat sheets and notes, with this tool you can get accurate answers right in your terminal, and you'll probably find yourself reducing your daily Google searches, saving you valuable time and effort. ShellGPT is cross-platform compatible and supports all major operating systems, including Linux, macOS, and Windows with all major shells, such as PowerShell, CMD, Bash, Zsh, Fish, and many others.

## Installation
```shell
pip install git+https://github.com/aeP6na/shell_gpt.git
```

## Usage (Shell commands)
Have you ever found yourself forgetting common shell commands, such as `chmod`, and needing to look up the syntax online? With sgptr, you can quickly find and execute the commands you need right in the terminal.
```shell
sgptr "make all files in current directory read only"
# -> chmod 444 *
# -> [E]xecute, [M]odify, [A]bort: e
...
```
sgptr is aware of OS and `$SHELL` you are using, it will provide shell command for specific system you have. For instance, if you ask `sgptr` to update your system, it will return a command based on your OS. Here's an example using macOS:
```shell
sgptr "update my system"
# -> sudo softwareupdate -i -a
# -> [E]xecute, [M]odify, [A]bort: e
...
```
The same prompt, when used on Ubuntu, will generate a different suggestion:
```shell
sgptr "update my system"
# -> sudo apt update && sudo apt upgrade -y
# -> [E]xecute, [M]odify, [A]bort: e
...
```
Let's try some docker containers:
```shell
sgptr "start nginx using docker, forward 443 and 80 port, mount current folder with index.html"
# -> docker run -d -p 443:443 -p 80:80 -v $(pwd):/usr/share/nginx/html nginx
# -> [E]xecute, [M]odify, [A]bort: e
...
```
We can use pipes to pass input to `sgptr` and get shell commands as output:
```shell
cat data.json | sgptr "curl localhost with provided json"
# -> curl -X POST -H "Content-Type: application/json" -d '{"a": 1, "b": 2, "c": 3}' http://localhost
```
We can apply additional shell magic in our prompt, in this example passing file names to ffmpeg:
```shell
ls
# -> 1.mp4 2.mp4 3.mp4
sgptr "using ffmpeg combine multiple videos into one without audio. Video file names: $(ls -m)"
# -> ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -filter_complex "[0:v] [1:v] [2:v] concat=n=3:v=1 [v]" -map "[v]" out.mp4
# -> [E]xecute, [M]odify, [A]bort: e
...
```

### Shell integration
Shell integration allows you to use sgptr in your terminal with hotkeys. It is currently available for bash and zsh. It will allow you to have sgptr completions in your shell history, and also edit suggested commands right away.

To install shell integration, run:
```shell
sgptr --install-integration
# Restart your terminal to apply changes.
```
This will add few lines to your `.bashrc` or `.zshrc` file. After that, you can use `Ctrl+i` (by default) to invoke sgptr. When you press `Ctrl+i` it will replace you current input line (buffer) with suggested command. You can then edit it and press `Enter` to execute.

### Runtime configuration file
You can setup some parameters in runtime configuration file `~/.config/shell_gptr/.sgptrc`:
```text
# API host, this the url of our server.
API_HOST=http://localhost:7070
# Request cache length (amount).
CACHE_LENGTH=100
# Request cache folder.
CACHE_PATH=/tmp/shell_gpt/cache
# Request timeout in seconds.
REQUEST_TIMEOUT=60
# Default color for completions.
DEFAULT_COLOR=magenta
# Default to "A" for no input.
DEFAULT_EXECUTE_SHELL_CMD=false
```
Possible options for `DEFAULT_COLOR`: black, red, green, yellow, blue, magenta, cyan, white, bright_black, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white.
