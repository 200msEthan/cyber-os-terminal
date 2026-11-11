# Contributing to CYBER-OS Terminal

Thank you for your interest in contributing to **CYBER-OS // Neural Terminal & Security Arsenal**!

## Design Principles
1. **Zero Mandatory Python Dependencies**: All core features in `scifi_hud.py` and `cyber_tools.py` must run using Python's standard library (`>=3.8`) so the suite works out-of-the-box on any fresh Linux, macOS, or Windows installation.
2. **Cross-Platform Compatibility**: New telemetry or security modules should degrade gracefully across **Linux**, **macOS (`Darwin`)**, and **Windows**.
3. **24-Bit TrueColor Cyberpunk Aesthetic**: Maintain the Neon Magenta (`#ff00a0`), Electric Cyan (`#00f3ff`), and Matrix Mint (`#00ff9f`) visual language and 86-column inner box alignment (`BOX_INNER_WIDTH = 86`).

## Development Workflow
1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feat/my-cyber-module
   ```
2. Test all HUD and CLI flags across your changes:
   ```bash
   python3 scifi_hud.py
   python3 cyber_tools.py --jobs
   python3 cyber_tools.py --ports 127.0.0.1
   python3 cyber_tools.py --audit
   ```
3. Commit your changes with a clear message and open a Pull Request!
