# Contributing to CYBER-OS Terminal

Thanks for helping build **CYBER-OS // Neural Terminal & Security Arsenal**! First-time contributors are very welcome — many issues are small and self-contained on purpose.

## Finding something to work on

- [`good first issue`](https://github.com/abhisek11/cyber-os-terminal/labels/good%20first%20issue) — small, well-scoped, with the file and a test command listed.
- [`help wanted`](https://github.com/abhisek11/cyber-os-terminal/labels/help%20wanted) — bigger features where a hand is appreciated.
- `platform: windows` / `platform: macos` — if you use one of these, you can help a lot just by testing.

Comment **"I'd like to work on this"** on the issue before starting so two people don't build the same thing. If an assigned issue sees no activity for two weeks it may be reassigned.

## Project layout

| File | What it does |
| :--- | :--- |
| `scifi_hud.py` | Telemetry HUD, `--watch`, `--matrix`, `--scan` |
| `cyber_tools.py` | Security toolkit + interactive menu (`cyber-tools`) |
| `cyber_search.py` | File / browser-history / web search |
| `cyber_vision.py` | Camera, gesture, ASL and voice web cockpit |
| `cyberpunk_shell.sh`, `cyberpunk_profile.ps1` | Aliases and prompt for bash/zsh and PowerShell |
| `install.sh`, `install.ps1` | Installers |
| `starship.toml`, `tmux.cyberpunk.conf` | Prompt and tmux themes |

## Design principles

1. **Zero mandatory Python dependencies.** Core features in `scifi_hud.py`, `cyber_tools.py` and `cyber_search.py` must run on Python's standard library (`>=3.8`). Optional extras must degrade gracefully when missing.
2. **Cross-platform.** New features should work, or fail politely, on Linux, macOS (`Darwin`) and Windows.
3. **The look.** Keep the Neon Magenta `#ff00a0`, Electric Cyan `#00f3ff` and Matrix Mint `#00ff9f` palette, and keep box rows inside `BOX_INNER_WIDTH = 86` — use `box_row()` and `visible_len()` rather than counting characters yourself.
4. **Safe by default.** Anything destructive (killing processes, writing files) should be explicit and easy to understand.

## Development workflow

```bash
git clone https://github.com/<you>/cyber-os-terminal.git
cd cyber-os-terminal
git checkout -b fix/short-description

# Smoke-test what you touched
python3 scifi_hud.py
python3 cyber_tools.py --jobs
python3 cyber_tools.py --ports 127.0.0.1
python3 cyber_tools.py --audit
python3 -m py_compile *.py
```

Then commit with a clear message (`fix: ...`, `feat: ...`, `docs: ...`), push, and open a Pull Request that links the issue (`Closes #12`). Add a screenshot for anything visual.

## Code of Conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
