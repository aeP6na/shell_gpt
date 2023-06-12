import platform
from os import getenv, pathsep
from os.path import basename
from typing import Dict

from distro import name as distro_name

class SystemRole:

    @classmethod
    def os_name(cls) -> str:
        current_platform = platform.system()
        if current_platform == "Linux":
            return "Linux/" + distro_name(pretty=True)
        if current_platform == "Windows":
            return "Windows " + platform.release()
        if current_platform == "Darwin":
            return "Darwin/MacOS " + platform.mac_ver()[0]
        return current_platform

    @classmethod
    def shell_name(cls) -> str:
        current_platform = platform.system()
        if current_platform in ("Windows", "nt"):
            is_powershell = len(getenv("PSModulePath", "").split(pathsep)) >= 3
            return "powershell.exe" if is_powershell else "cmd.exe"
        return basename(getenv("SHELL", "/bin/sh"))

    @classmethod
    def get_variables(cls) -> Dict[str, str]:
        return {"shell": cls.shell_name(), "os": cls.os_name()}
    