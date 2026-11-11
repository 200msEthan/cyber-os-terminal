#!/usr/bin/env bash
# ============================================================================
# CYBER-OS // CROSS-PLATFORM SCI-FI TERMINAL INSTALLER (LINUX, MACOS, WSL)
# Usage:
#   bash install.sh              # Configure .bashrc & .zshrc
#   bash install.sh --packages   # Install cyber & sci-fi CLI packages (apt / brew / dnf / pacman)
#   bash install.sh --uninstall  # Restore original shell config
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKER_BEGIN="# >>> CYBER-OS SCI-FI TERMINAL >>>"
MARKER_END="# <<< CYBER-OS SCI-FI TERMINAL <<<"

CYAN="\033[38;2;0;243;255m"
MAGENTA="\033[38;2;255;0;160m"
GREEN="\033[38;2;0;255;159m"
YELLOW="\033[38;2;252;238;10m"
RESET="\033[0m"
BOLD="\033[1m"

chmod +x "${SCRIPT_DIR}/scifi_hud.py" "${SCRIPT_DIR}/cyber_tools.py" "${SCRIPT_DIR}/cyberpunk_shell.sh"

remove_block() {
    local rc_file="$1"
    if [[ -f "$rc_file" ]] && grep -q "$MARKER_BEGIN" "$rc_file"; then
        if [[ "$(uname -s)" == "Darwin" ]]; then
            sed -i '' "/${MARKER_BEGIN}/,/${MARKER_END}/d" "$rc_file"
        else
            sed -i "/${MARKER_BEGIN}/,/${MARKER_END}/d" "$rc_file"
        fi
    fi
}

install_block() {
    local rc_file="$1"
    if [[ ! -f "$rc_file" ]]; then
        touch "$rc_file"
    fi
    cp "$rc_file" "${rc_file}.cyber_backup" 2>/dev/null || true
    remove_block "$rc_file"
    cat >> "$rc_file" <<EOF

${MARKER_BEGIN}
if [ -f "${SCRIPT_DIR}/cyberpunk_shell.sh" ]; then
    source "${SCRIPT_DIR}/cyberpunk_shell.sh"
fi
${MARKER_END}
EOF
    echo -e "  ${GREEN}✔ Configured:${RESET} ${rc_file}"
}

if [[ "$1" == "--uninstall" ]]; then
    echo -e "${MAGENTA}⚡ Removing Cyber-OS Sci-Fi Terminal hooks...${RESET}"
    remove_block "$HOME/.bashrc"
    remove_block "$HOME/.bash_profile"
    remove_block "$HOME/.zshrc"
    echo -e "${GREEN}✔ Uninstalled cleanly.${RESET}"
    exit 0
fi

echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${MAGENTA}║${RESET} ${CYAN}${BOLD}⚡ INSTALLING CYBER-OS NEON TERMINAL SUITE (LINUX / MACOS / WSL)${RESET}     ${MAGENTA}║${RESET}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════════════╝${RESET}"

install_block "$HOME/.bashrc"
if [[ "$(uname -s)" == "Darwin" ]]; then
    install_block "$HOME/.bash_profile"
fi
if [[ -f "$HOME/.zshrc" ]] || command -v zsh >/dev/null 2>&1; then
    install_block "$HOME/.zshrc"
fi

mkdir -p "$HOME/.config"
cp "${SCRIPT_DIR}/starship.toml" "$HOME/.config/starship.toml"
echo -e "  ${GREEN}✔ Installed Starship Neon Config:${RESET} $HOME/.config/starship.toml"

if [[ "$1" == "--packages" ]]; then
    echo -e "\n${CYAN}❖ Installing Sci-Fi & Cyber Security CLI Arsenal...${RESET}"
    if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
        brew install btop bat fzf eza tmux starship nmap whois bind netcat
    elif command -v sudo >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -y
        sudo apt-get install -y btop bat fzf tmux eza nmap whois dnsutils netcat-openbsd tcpdump curl openssl 2>/dev/null \
            || sudo apt-get install -y btop bat fzf tmux nmap whois dnsutils netcat-openbsd tcpdump curl openssl
    elif command -v sudo >/dev/null 2>&1 && command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y btop bat fzf tmux nmap whois bind-utils nmap-ncat tcpdump curl openssl
    elif command -v sudo >/dev/null 2>&1 && command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm btop bat fzf tmux eza nmap whois bind openbsd-netcat tcpdump curl openssl
    fi

    if ! command -v starship >/dev/null 2>&1; then
        mkdir -p "$HOME/.local/bin"
        curl -sS https://starship.rs/install.sh | sh -s -- -b "$HOME/.local/bin" -y
    fi
fi

echo -e "\n${YELLOW}⚡ PREVIEWING CYBER-OS TELEMETRY HUD:${RESET}\n"
python3 "${SCRIPT_DIR}/scifi_hud.py" --boot

echo -e "\n${GREEN}${BOLD}✔ INSTALLATION COMPLETE!${RESET}"
echo -e "  Run: ${CYAN}${BOLD}source ~/.bashrc${RESET} (or ${CYAN}${BOLD}source ~/.zshrc${RESET} on macOS) to activate immediately."
