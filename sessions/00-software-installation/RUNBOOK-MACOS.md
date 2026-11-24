# Session 00 — Install the software on macOS

Use **Terminal** for the commands below. Press **Command+Space**, type
`Terminal`, and open it. Paste one command at a time and press **Return**.
The default macOS shell is zsh. Install VS Code, Git, and Python before
Session 01. Docker Desktop is used from the Session 10 database lab onward.
The first two sessions run locally without Docker or provider credentials.

Open **Apple menu → About This Mac**. If it shows an Apple chip, choose
**Apple silicon** downloads. If it shows an Intel processor, choose **Intel**.
A Universal VS Code build works on both. [VS Code for macOS](https://code.visualstudio.com/docs/setup/mac)

## 1. Install VS Code

1. Download the macOS build, open the download, and drag
   **Visual Studio Code.app** into **Applications**.
2. Open VS Code from Applications. Press **Command+Shift+X** and install
   **Python** by **Microsoft** from Extensions.
3. To enable the optional `code .` shortcut, press **Command+Shift+P**, run
   **Shell Command: Install 'code' command in PATH**, and reopen Terminal.
   You can also use **File → Open Folder** without this shortcut.

[Official VS Code macOS instructions](https://code.visualstudio.com/docs/setup/mac)

## 2. Install Git

Use Apple's Command Line Tools. Run the install command if Git is missing
or macOS asks for the tools. In the macOS dialog, choose **Install** and wait
for it to finish. Verify in Terminal:

```bash
xcode-select --install
git --version
```

If macOS says the tools are already installed, continue with the Git version
check. [Git installation on macOS](https://git-scm.com/install/mac)

### Set up GitHub access

Git tracks changes on your computer. GitHub hosts the course repository
online. Use a GitHub account in your browser and install GitHub CLI (`gh`)
for terminal sign-in.

1. Sign in to GitHub, or create an account and verify your email address.
2. Give your GitHub username to the instructor. Accept the invitation to the
   private course repository while signed in with that account.

[GitHub account setup](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account) ·
[Repository invitations](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

### Install GitHub CLI and sign in

If you already have Homebrew, run:

```bash
brew --version
brew install gh
```

If `brew` is missing, follow the official Homebrew installation instructions
and the terminal's **Next steps** to put it on your shell path. Open a new
Terminal, then run the two commands above. [Homebrew installation](https://brew.sh/) ·
[GitHub CLI installation options](https://cli.github.com/)

Open a fresh terminal. Run the commands in order. When GitHub CLI displays
a one-time code and opens the browser, complete authorization with the same
account that accepted the invitation.

```bash
gh --version
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
gh auth setup-git --hostname github.com
git ls-remote --exit-code https://github.com/amity1415/servicedesk-copilot-cohort.git refs/heads/codex/project-session-setup
```

The last command should print a commit ID and
`refs/heads/codex/project-session-setup`. If GitHub reports that the repository
cannot be found, confirm the account shown by `gh auth status` and check that
you accepted the course invitation. Continue to Python setup after the check
passes.

[GitHub CLI sign-in](https://cli.github.com/manual/gh_auth_login) ·
[Git credentials with GitHub CLI](https://cli.github.com/manual/gh_auth_setup-git)

## 3. Install Python

The project requires Python **3.12 or newer**. This guide uses standard
**CPython 3.14**.

1. Open the official macOS releases page and select a stable **Python 3.14.x**
   release with a **macOS 64-bit universal2 installer**.
2. Open the downloaded `.pkg` and follow the installation prompts.
3. Close and reopen Terminal. Check which Python is available:

```bash
command -v python3.14
python3.14 --version
```

If package installation reports a certificate error after a Python.org
install, open Finder → Applications → Python 3.14 and run
**Install Certificates.command**, then retry. If you already have a working
Python 3.12–3.14, you may use its corresponding command to create the
environment below. [Official Python macOS downloads](https://www.python.org/downloads/macos/) ·
[Using Python on macOS](https://docs.python.org/3/using/mac.html)

## 4. Get the course and verify the environment

Use a GitHub account with access to the private course repository. The clone
command is for a fresh checkout. If you already have one, use `cd` to go to its
root and start at `ls pyproject.toml`.

```bash
cd "$HOME"
git clone --branch codex/project-session-setup --single-branch https://github.com/amity1415/servicedesk-copilot-cohort.git servicedesk-copilot
cd servicedesk-copilot
ls pyproject.toml
test -x .venv/bin/python || python3.14 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install -e ".[dev,ticketing,course]"
python -m pip check
python scripts/session.py run 1
python scripts/session.py test 1
```

In a new terminal, use `cd "$HOME/servicedesk-copilot"` and
`source .venv/bin/activate` again. You can also invoke `./.venv/bin/python`
directly.

Expect Python 3.14.x on the install path above, a successful dependency
check, **5,000 tickets** from the example, and **17 passing tests**. These
commands use the bundled synthetic data and the completed Session 01 solution.

In VS Code, choose **File → Open Folder** and open the checkout. Open the
Command Palette, choose **Python: Select Interpreter**, and select the
interpreter in `.venv`. Keep the terminal at the repository root when running
course commands. [VS Code Python setup](https://code.visualstudio.com/docs/python/python-tutorial)

## 5. Install Docker Desktop and check Compose

1. Download the Docker Desktop build for the chip recorded at the start.
2. Open `Docker.dmg`, drag **Docker.app** to **Applications**, then launch it
   from Applications. Follow the setup prompts and wait for the engine to start.
3. Open a fresh Terminal and run:

```bash
docker version
docker compose version
docker run --rm hello-world
```

If `docker` is missing, check Docker Desktop's CLI tools installation option,
then reopen Terminal. On a managed Mac, use your organization's approved
installation and licensing arrangements.
[Docker Desktop for Mac installation](https://docs.docker.com/desktop/setup/install/mac-install/)

Before opening the later runbooks, remember that their examples use PowerShell.
For the basic session commands, activate `.venv` and replace `& $py` with
`python`. Replace `Get-Location` with `pwd`, `Get-Item` with `ls`,
and `Get-Content <file>` with `cat <file>` or `head <file>`. Use
`export NAME='value'` for environment settings. Git and Docker commands stay
the same.

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
