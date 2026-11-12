#!/usr/bin/env bash
# ============================================================================
# CYBER-OS // NEURAL SHELL PROFILE (BASH & ZSH COMPATIBLE)
# Palette: Cyberpunk Neon (Electric Cyan, Neon Magenta, Synthwave Purple)
# ============================================================================

# Only run in interactive shells
case $- in
    *i*) ;;
      *) return ;;
esac

CYBER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
export STARSHIP_CONFIG="${CYBER_DIR}/starship.toml"

# Ensure ~/.local/bin is in PATH (for starship, eza, etc.)
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# ----------------------------------------------------------------------------
# 1. BUILT-IN SCI-FI COMMANDS & CYBER SECURITY ARSENAL
# ----------------------------------------------------------------------------
alias hud="python3 '${CYBER_DIR}/scifi_hud.py'"
alias cyber-watch="python3 '${CYBER_DIR}/scifi_hud.py' --watch"
alias cyber-matrix="python3 '${CYBER_DIR}/scifi_hud.py' --matrix"
alias cyber-scan="python3 '${CYBER_DIR}/scifi_hud.py' --scan"

# Interactive Cyber-Deck Security & Recon Menu
alias cyber-tools="python3 '${CYBER_DIR}/cyber_tools.py' --menu"
alias cyber-jobs="python3 '${CYBER_DIR}/cyber_tools.py' --jobs"
alias cyber-conn="python3 '${CYBER_DIR}/cyber_tools.py' --conn"
alias cyber-audit="python3 '${CYBER_DIR}/cyber_tools.py' --audit"
alias cyber-arsenal="python3 '${CYBER_DIR}/cyber_tools.py' --arsenal"

# Parameterized Cyber CLI Functions
cyber-ports() {
    python3 "${CYBER_DIR}/cyber_tools.py" --ports "${1:-127.0.0.1}" --range "${2:-common}"
}
cyber-kill() {
    if [[ -z "$1" ]]; then
        echo -e "\033[38;2;255;42;109m✖ Usage: cyber-kill <PORT> (e.g. cyber-kill 8000)\033[0m"
        return 1
    fi
    python3 "${CYBER_DIR}/cyber_tools.py" --kill-port "$1" --force
}
cyber-recon() {
    python3 "${CYBER_DIR}/cyber_tools.py" --recon "${1:-example.com}"
}
cyber-ssl() {
    python3 "${CYBER_DIR}/cyber_tools.py" --ssl "${1:-github.com}"
}
cyber-headers() {
    python3 "${CYBER_DIR}/cyber_tools.py" --headers "${1:-https://github.com}"
}
cyber-hash() {
    python3 "${CYBER_DIR}/cyber_tools.py" --hash "${1:-cyberdeck}"
}
cyber-decode() {
    python3 "${CYBER_DIR}/cyber_tools.py" --decode "$1"
}
cyber-keygen() {
    python3 "${CYBER_DIR}/cyber_tools.py" --keygen "${1:-32}"
}
cyber-fim() {
    python3 "${CYBER_DIR}/cyber_tools.py" --fim "${1:-.}"
}
cyber-secrets() {
    python3 "${CYBER_DIR}/cyber_tools.py" --secrets "${1:-.}"
}
cyber-nmap() {
    python3 "${CYBER_DIR}/cyber_tools.py" --nmap "${1:-127.0.0.1}"
}

# Neural Camera Vision (Face ID, Hand Gestures, ASL Sign Language & Voice Cockpit)
cyber-cam() {
    python3 "${CYBER_DIR}/cyber_vision.py" "$@"
}

# Omni-Search Engine (Local Files + Browser History + Live Internet/Web)
cyber-search() {
    python3 "${CYBER_DIR}/cyber_search.py" --omni "${*:-cyber}"
}
cyber-find() {
    python3 "${CYBER_DIR}/cyber_search.py" --files "${1:-cyber}" --dir "${2:-.}"
}
cyber-history() {
    python3 "${CYBER_DIR}/cyber_search.py" --history "${*:-recent}"
}
cyber-web() {
    python3 "${CYBER_DIR}/cyber_search.py" --web "${*:-cybersecurity}"
}

# Cockpit multiplexer launcher (uses tmux with cyberpunk config if installed, else live HUD)
cyber-cockpit() {
    if command -v tmux >/dev/null 2>&1; then
        tmux -f "${CYBER_DIR}/tmux.cyberpunk.conf" new-session -A -s cyberdeck \
            "python3 '${CYBER_DIR}/scifi_hud.py' --watch" \; \
            split-window -h -p 60 \; \
            select-pane -t 1
    else
        python3 "${CYBER_DIR}/scifi_hud.py" --watch
    fi
}

# ----------------------------------------------------------------------------
# 2. SMART NEXT-GEN CLI REPLACEMENTS
# ----------------------------------------------------------------------------
if command -v eza >/dev/null 2>&1; then
    alias ls='eza --icons --group-directories-first --color=always'
    alias ll='eza -lah --icons --group-directories-first --git'
    alias la='eza -a --icons --group-directories-first'
    alias lt='eza --tree --level=2 --icons'
elif command -v lsd >/dev/null 2>&1; then
    alias ls='lsd --group-dirs=first'
    alias ll='lsd -lah --group-dirs=first'
    alias la='lsd -A --group-dirs=first'
    alias lt='lsd --tree --depth=2'
else
    alias ls='ls --color=auto --group-directories-first'
    alias ll='ls -lah --color=auto --group-directories-first'
    alias la='ls -A --color=auto --group-directories-first'
fi

if command -v batcat >/dev/null 2>&1; then
    alias cat='batcat --style=numbers,changes --color=always --paging=never'
    alias bat='batcat'
elif command -v bat >/dev/null 2>&1; then
    alias cat='bat --style=numbers,changes --color=always --paging=never'
fi

if command -v btop >/dev/null 2>&1; then
    alias top='btop'
elif command -v htop >/dev/null 2>&1; then
    alias top='htop'
fi

alias grep='grep --color=auto'
alias df='df -h'
alias free='free -h'
alias ports='ss -tulanp'
alias glog='git log --graph --oneline --decorate --all --color=always'
alias gs='git status -sb'

# ----------------------------------------------------------------------------
# 3. CYBERPUNK NEON PROMPT (STARSHIP OR BUILT-IN TRUECOLOR FALLBACK)
# ----------------------------------------------------------------------------
_cyber_git_branch() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [[ -n "$branch" ]]; then
        local dirty=""
        if [[ -n $(git status --porcelain 2>/dev/null | head -n 1) ]]; then
            dirty=" ⚡"
        fi
        printf "═[  %s%s ]" "$branch" "$dirty"
    fi
}

_cyber_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        printf "═[ 🐍 %s ]" "$(basename "$VIRTUAL_ENV")"
    fi
}

if command -v starship >/dev/null 2>&1; then
    if [[ -n "$ZSH_VERSION" ]]; then
        eval "$(starship init zsh)"
    elif [[ -n "$BASH_VERSION" ]]; then
        eval "$(starship init bash)"
    fi
else
    # Pure TrueColor Cyberpunk Neon Fallback Prompt (Zero extra packages required!)
    if [[ -n "$BASH_VERSION" ]]; then
        _cyber_bash_prompt() {
            local exit_code=$?
            local c_reset='\[\e[0m\]'
            local c_cyan='\[\e[1;38;2;0;243;255m\]'
            local c_mag='\[\e[1;38;2;255;0;160m\]'
            local c_purple='\[\e[1;38;2;189;0;255m\]'
            local c_yellow='\[\e[1;38;2;252;238;10m\]'
            local c_green='\[\e[1;38;2;0;255;159m\]'
            local c_red='\[\e[1;38;2;255;42;109m\]'
            local c_blue='\[\e[1;38;2;90;100;255m\]'

            local arrow_color="$c_cyan"
            if [[ $exit_code -ne 0 ]]; then
                arrow_color="$c_red"
            fi

            local git_seg
            git_seg="$(_cyber_git_branch)"
            local venv_seg
            venv_seg="$(_cyber_venv)"

            PS1="\n${c_mag}╔═[${c_cyan}⚡ \u${c_purple}@\h${c_mag}]═[${c_yellow} ◈ \w ${c_mag}]${c_green}${git_seg}${c_cyan}${venv_seg}${c_blue}═[ ⌚ \t ]${c_reset}\n${c_mag}╚═${arrow_color}◢◤ ${c_mag}❯${c_reset} "
        }
        PROMPT_COMMAND="_cyber_bash_prompt"
    elif [[ -n "$ZSH_VERSION" ]]; then
        setopt PROMPT_SUBST
        PROMPT=$'\n%{\e[1;38;2;255;0;160m%}╔═[%{\e[1;38;2;0;243;255m%}⚡ %n%{\e[1;38;2;189;0;255m%}@%m%{\e[1;38;2;255;0;160m%}]═[%{\e[1;38;2;252;238;10m%} ◈ %~ %{\e[1;38;2;255;0;160m%}]%{\e[1;38;2;0;255;159m%}$(_cyber_git_branch)%{\e[1;38;2;0;243;255m%}$(_cyber_venv)%{\e[1;38;2;90;100;255m%}═[ ⌚ %* ]%{\e[0m%}\n%{\e[1;38;2;255;0;160m%}╚═%(?.%{\e[1;38;2;0;243;255m%}.%{\e[1;38;2;255;42;109m%})◢◤ %{\e[1;38;2;255;0;160m%}❯%{\e[0m%} '
    fi
fi

# ----------------------------------------------------------------------------
# 4. LAUNCH CYBERPUNK STARTUP TELEMETRY HUD
# ----------------------------------------------------------------------------
if [[ -z "$CYBER_HUD_SHOWN" ]]; then
    export CYBER_HUD_SHOWN=1
    python3 "${CYBER_DIR}/scifi_hud.py" --boot
fi
