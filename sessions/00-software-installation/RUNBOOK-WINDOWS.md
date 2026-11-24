# Session 00 — Install the software on Windows

Use **PowerShell** for the commands below. Open it from the Start menu, paste
one command at a time, and press **Enter**. Install VS Code, Git, and Python
before Session 01. Docker Desktop is used for the database lab in Session 10
and later service labs. The first two sessions run locally without Docker or
provider credentials.

Check **Settings → System → About → System type** before downloading
installers. Choose the download matching your processor. If this is a work
machine, use the software distribution and Docker licensing arrangements
approved by your organization. [Docker Desktop for Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/)

## 1. Install VS Code

1. Download the **Windows User Installer**.
2. Run it. Leave **Add to PATH** enabled if the installer offers it.
3. Open VS Code from Start. Press **Ctrl+Shift+X** to open Extensions.
4. Search for **Python** and install the extension published by **Microsoft**.
5. Close and reopen PowerShell after installing.

[Official VS Code installer and instructions](https://code.visualstudio.com/docs/setup/windows)

## 2. Install Git

Download and run Git for Windows. During setup, select the option that makes
Git available to PowerShell and other command-line tools. Open a fresh
PowerShell window and check:

```powershell
git --version
```

[Official Git for Windows download](https://git-scm.com/install/win)

## 3. Install Python

The project requires Python **3.12 or newer**. This guide uses standard
**CPython 3.14** so the install and verification commands name the same
version.

1. Download the **Python Install Manager** from Python.org and install it.
2. Open a new PowerShell window and install and verify Python:

```powershell
py install 3.14
py -3.14 --version
```

If `py` is missing, reopen PowerShell and verify the manager installed. If
`py install` opens a file error, a legacy launcher may have priority. See
the official troubleshooting steps. If you already have a working Python
3.12–3.14 and wish to reuse it, use that version selector in the venv command
below. [Python on Windows](https://docs.python.org/3/using/windows.html) ·
[Official Windows downloads](https://www.python.org/downloads/windows/)

## 4. Get the course and verify the environment

Sign in to GitHub with the account that has access to the private course
repository. The clone command below is for a fresh checkout. If you already
have the repository, skip the clone and use `Set-Location` to go to its root.
Use a short path on Windows.

```powershell
Set-Location $env:USERPROFILE
git clone --branch codex/project-session-setup --single-branch https://github.com/amity1415/servicedesk-copilot-cohort.git servicedesk-copilot
Set-Location servicedesk-copilot
Get-Item pyproject.toml
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { py -3.14 -m venv .venv }
$py = '.\.venv\Scripts\python.exe'
& $py --version
& $py -m pip install -e ".[dev,ticketing,course]"
& $py -m pip check
& $py scripts/session.py run 1
& $py scripts/session.py test 1
```

The direct `& $py` commands work without activating the environment. Set
`$py = '.\.venv\Scripts\python.exe'` again if you open a new PowerShell window.

Expect Python 3.14.x on the install path above, a successful dependency
check, **5,000 tickets** from the example, and **17 passing tests**. These
commands use the bundled synthetic data and the completed Session 01 solution.

In VS Code, choose **File → Open Folder** and open the checkout. Open the
Command Palette, choose **Python: Select Interpreter**, and select the
interpreter in `.venv`. Keep the terminal at the repository root when running
course commands. [VS Code Python setup](https://code.visualstudio.com/docs/python/python-tutorial)

## 5. Install Docker Desktop and check Compose

1. Check whether WSL is available with `wsl --version`. If WSL is missing,
   open **PowerShell as Administrator** and run the install command below.
   Restart if Windows asks. If WSL is already installed, run the update command
   as needed.

```powershell
wsl --install --no-distribution
wsl --update
wsl --version
```

2. Download **Docker Desktop for Windows**. Run the installer and choose the
   **WSL 2** backend if prompted.
3. Start Docker Desktop from the Start menu and wait for the engine to start.
   Use the Linux container engine for the course.
4. In a fresh PowerShell window, run the three checks:

```powershell
docker version
docker compose version
docker run --rm hello-world
```

[Microsoft WSL installation](https://learn.microsoft.com/windows/wsl/install) ·
[Docker Desktop for Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)

Docker downloads the small hello-world image on the first run. Look for
`Hello from Docker!`. If the client cannot connect to the engine, open
Docker Desktop, wait for startup, and retry. If pulling the image fails,
check the connection to Docker Hub or your organization's proxy settings.

## 6. Continue to Session 01

Git, Python, VS Code, and the successful course smoke check are enough to
begin. Save the Docker check for before Session 10 if you are deferring that
installation. Compose starts the teaching PostgreSQL/pgvector database and
later mock services, so you can use those without installing PostgreSQL
separately.

[Session 01 runbook](../01-kickoff-and-project-setup/RUNBOOK.md) ·
[All session runbooks](../SETUP.md) ·
[Full project setup](../../docs/PROJECT_SETUP.md)
