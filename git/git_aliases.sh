#!/bin/bash

alias gichepi="git cherry-pick"

# DIFF
alias gidif_setgui="git config --global diff.external meldiff.py"
alias gidif_setcmd="git config --global --unset diff.external"
alias gidif="git diff"

# SHOW
alias gisho="git show"
gishogui(){
  # mvtodo: does not work on the first commit of a repository
  HASH=$1
  if [ -z $1 ]; then
    HASH="HEAD"
  fi
  git difftool -y --no-prompt $HASH~1 $HASH
}

gikill(){
  if [ ! -d "$HOME/nuke" ]; then
    echo "No $HOME/nuke folder found. Aborting."
    return
  fi
  git show > ~/nuke/gikill_backup.patch
  git reset --hard HEAD~$1
}

alias gista="git status"
alias giadd="git add"
alias giunadd="git reset HEAD"
alias gicom="git_commit_with_prechecks.py"
alias gilog="git log"
alias gipus="git push"
alias gipul="git pull --ff-only"
alias giclo="git clone"
alias gibra="git branch"
alias giche="git checkout"
alias gires="git reset"
alias gimer="git merge"
alias gifet="git fetch"
alias gitag="git tag"
alias gisub="git submodule"
alias gibis="git bisect"
alias giapp="git apply"
alias gides="git describe"
alias giini="git init"
alias gicon="git config"
alias gireb="git rebase"
alias girem="git remote -v"
alias gigre="git grep -n"
alias gihel="git help"
alias gibla="git blame"
alias gistash="git stash"
alias giver="git version"
alias gicle="git clean"
alias gifsck="git fsck"

alias gimv="git mv"
alias girm="git rm"

