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

# COMMIT
alias gicom="git commit" # mvtodo: add mvtags checking as a precondition

alias gista="git status"
alias giadd="git add"
alias girem="git rm"
alias gilog="git log"
alias gipus="git push"
alias gipul="git pull"
alias giclo="git clone"
alias gibra="git branch"
alias giche="git checkout"
alias gires="git reset"
alias gimer="git merge"
alias gifet="git fetch"
alias gitag="git tag"
alias gisub="git submodule"
alias gireb="git rebase"
alias gibis="git bisect"
alias giapp="git apply"
alias gides="git describe"
alias giini="git init"
alias gicon="git config"
alias gitag="git tag"
alias gireb="git rebase"
alias girem="git remote"
alias gigre="git grep -n"
alias gihel="git help"
alias gibla="git blame"
alias gistash="git stash"
alias giver="git version"

alias gimv="git mv"
alias girm="git rm"

