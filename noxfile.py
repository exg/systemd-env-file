import nox

nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = [
    "3.9",
    "3.10",
    "3.11",
    "3.12",
]


@nox.session(python=PYTHON_VERSIONS[0])
def lint(session: nox.Session) -> None:
    session.install(".[dev,test]")
    session.run("ruff", "format", "--check", "src", "tests")
    session.run("ruff", "check", "src", "tests")
    session.run("mypy", "src")


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    session.install(".[test]")
    session.run(
        "pytest",
        "--cov=systemd_env_file",
        "tests",
    )
