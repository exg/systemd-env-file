# systemd environment file parser

systemd-env-file is a pure Python port of the systemd parser for the
[EnvironmentFile](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=)
format.

## Usage

```python
from systemd_env_file import load
with open("env_file") as f:
    env = load(f)
```
