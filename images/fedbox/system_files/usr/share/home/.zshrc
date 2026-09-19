if [ ! -f $HOME/.p10k.zsh ]; then
  cp /usr/share/home/.p10k.zsh $HOME
fi

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
export PATH=/usr/local/go/bin:$HOME/go/bin:$HOME/bin:$PATH
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Load a plugin: resolve it from the user dir ($ZPLUGINDIR, persistent in the
# home volume) or the image dir ($ZPLUGINDIR_SYSTEM, pre-cloned at build time),
# identify its init file, source it, and add it to fpath. Plugins found in
# neither dir are cloned into the user dir, so user-installed plugins survive
# image updates and pod restarts. User plugins win over image plugins.
# Thanks to https://github.com/mattmc3/zsh_unplugged
typeset -A _LOADED_PLUGINS
function plugin-load {
  local repo plugdir initfile initfiles=()
  local userdir=${ZPLUGINDIR:-$HOME/.config/zsh/plugins}
  local sysdir=${ZPLUGINDIR_SYSTEM:-/nonexistent}
  mkdir -p "$userdir"
  for repo in $@; do
    if [[ -d $userdir/${repo:t} ]]; then
      plugdir=$userdir/${repo:t}
    elif [[ -d $sysdir/${repo:t} ]]; then
      plugdir=$sysdir/${repo:t}
    else
      echo "Cloning $repo..."
      git clone -q --depth 1 --recursive --shallow-submodules https://github.com/$repo $userdir/${repo:t} || continue
      plugdir=$userdir/${repo:t}
    fi
    (( $+_LOADED_PLUGINS[$plugdir] )) && continue   # never double-source
    initfile=$plugdir/${repo:t}.plugin.zsh
    if [[ ! -e $initfile ]]; then
      initfiles=($plugdir/*.{plugin.zsh,zsh-theme,zsh,sh}(N))
      (( $#initfiles )) || { echo >&2 "No init file found '$repo'." && continue }
      ln -sf $initfiles[1] $initfile
    fi
    _LOADED_PLUGINS[$plugdir]=1
    fpath+=$plugdir
    . $initfile
  done
}

# OMZ expects a list named 'plugins' so we can't use that variable name for repos,
# it can only contain the names of actual OMZ plugins
plugins=(
  git
  # copypath
  extract
  magic-enter
  docker
  kubectl
  fzf
)

repos=(
  romkatv/powerlevel10k
  ohmyzsh/ohmyzsh
  reegnz/jq-zsh-plugin
  Tarrasch/zsh-bd
  zsh-users/zsh-autosuggestions
  zsh-users/zsh-history-substring-search
  zsh-users/zsh-syntax-highlighting
)
plugin-load $repos

unset repos

HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_ALL_DUPS

### key bindings
bindkey '^[[1;5D' backward-word
bindkey '^[[1;5C' forward-word

### aliases
alias k=kubectl
if command -v eza >/dev/null 2>&1; then
  # eza as full replacement for interactive ls usage
  # (scripts keep /usr/bin/ls - aliases only apply in interactive shells)
  alias ls='eza --group-directories-first'
  alias l='eza -l --git'
  alias la='eza -a --group-directories-first'
  alias lla='eza -la --git'
  alias lt='eza --tree'
  # opt-in, needs a Nerd Font:
  # alias e='eza -la --git --icons'
else
  alias ls="ls --color"
  alias l='ls -l'
  alias la='ls -a'
  alias lla='ls -la'
fi

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# VTE/Tilix integration, only when available
if [ -n "$TILIX_ID" ] || [ -n "$VTE_VERSION" ]; then
  [[ -r /etc/profile.d/vte-2.91.sh ]] && source /etc/profile.d/vte-2.91.sh
fi

# Reuse a running ssh-agent instead of spawning one per shell
export SSH_AUTH_SOCK="$HOME/.ssh/ssh_auth_sock"
command ssh-add -l >/dev/null 2>&1
if [[ $? -gt 1 ]]; then  # 0/1 = agent reachable, 2 = no reachable agent
  eval "$(ssh-agent -s)"
  ln -sf "$SSH_AUTH_SOCK" "$HOME/.ssh/ssh_auth_sock"
  export SSH_AUTH_SOCK="$HOME/.ssh/ssh_auth_sock"
fi

alias jqs="jq '.data | map_values(@base64d)'"

export EDITOR="vim"
if [[ "$TERM_PROGRAM" == "vscode" ]]; then
  if [[ -x /usr/lib/code-server/lib/vscode/bin/remote-cli/code-server ]]; then
    export EDITOR="/usr/lib/code-server/lib/vscode/bin/remote-cli/code-server --wait"
  elif command -v code >/dev/null 2>&1; then
    export EDITOR="code --wait"
  fi
fi

# NVM: lazy-load; the default node version goes on PATH directly for fast startup
export NVM_DIR="$HOME/.nvm"
_node_default=$(command cat "$NVM_DIR/alias/default" 2>/dev/null)
if [[ -n "$_node_default" ]]; then
  _node_bin=$(command ls -d "$NVM_DIR/versions/node/v${_node_default}"* 2>/dev/null | tail -n 1)/bin
  [[ -d "$_node_bin" ]] && export PATH="$_node_bin:$PATH"
fi
unset _node_default _node_bin

nvm() {
  unset -f nvm
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
  nvm "$@"
}

lfcd () {
    tmp="$(mktemp)"
    # `command` is needed in case `lfcd` is aliased to `lf`
    command lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        dir="$(cat "$tmp")"
        rm -f "$tmp"
        if [ -d "$dir" ]; then
            if [ "$dir" != "$(pwd)" ]; then
                cd "$dir"
            fi
        fi
    fi
}
bindkey -s '^o' 'lfcd\n'

# Personal customizations belong in ~/.zshrc-local (inside the home volume),
# so they survive image updates - this file is replaced on every image build.
# A template with commented examples is installed as ~/.zshrc-local if missing.
[[ ! -f ~/.zshrc-local ]] || source ~/.zshrc-local
