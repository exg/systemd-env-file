# SPDX-License-Identifier: LGPL-2.1-or-later

from systemd_env_file import loads

ENV_FILE_1 = """
a=a
a=b
a=b
a=a
b=b\\
c
d= d\\
e  \\
f  
g=g\\ 
h= ąęół\\ śćńźżμ 
i=i\\
"""


def test_load_env_file_1() -> None:
    env = loads(ENV_FILE_1)
    assert env == {
        "a": "a",
        "b": "bc",
        "d": "de  f",
        "g": "g ",
        "h": "ąęół śćńźżμ",
        "i": "i",
    }


ENV_FILE_2 = """
a=a\\
"""


def test_load_env_file_2() -> None:
    env = loads(ENV_FILE_2)
    assert env == {
        "a": "a",
    }


ENV_FILE_3 = """
#SPAMD_ARGS=\"-d --socketpath=/var/lib/bulwark/spamd \\
#--nouser-config                                     \\
normal1=line\\
111
;normal=ignored                                      \\
normal2=line222
normal ignored                                       \\
"""


def test_load_env_file_3() -> None:
    env = loads(ENV_FILE_3)
    assert env == {
        "normal1": "line111",
        "normal2": "line222",
    }


ENV_FILE_4 = """
# Generated

HWMON_MODULES=\"coretemp f71882fg\"

# For compatibility reasons

MODULE_0=coretemp
MODULE_1=f71882fg
"""


def test_load_env_file_4() -> None:
    env = loads(ENV_FILE_4)
    assert env == {
        "HWMON_MODULES": "coretemp f71882fg",
        "MODULE_0": "coretemp",
        "MODULE_1": "f71882fg",
    }


ENV_FILE_5 = """
a=
b=
"""


def test_load_env_file_5() -> None:
    env = loads(ENV_FILE_5)
    assert env == {
        "a": "",
        "b": "",
    }


ENV_FILE_6 = """
a=\\ \\n \\t \\x \\y \\' 
b= \\$'                  
c= ' \\n\\t\\$\\`\\\\
'   
d= \" \\n\\t\\$\\`\\\\
\"   
"""


def test_load_env_file_6() -> None:
    env = loads(ENV_FILE_6)
    assert env == {
        "a": " n t x y '",
        "b": "$'",
        "c": " \\n\\t\\$\\`\\\\\n",
        "d": " \\n\\t$`\\\n",
    }
