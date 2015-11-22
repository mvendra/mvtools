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
  git reset --hard HEAD~$1
}

gicom(){
  TARGET=`pwd -P`
  TARGET=(`git_discover_repo_root.py $TARGET`) # resolve to the actual repo
  if [ $? -eq 1 ]; then
    # not a git repo. bail out.
    echo "This is not a git repository. Bailing out."
    return 1
  fi
  RESULT=(`test_mvtags_in_git_cache.py $TARGET`)
  if [ $? -eq 1 ]; then
    # a pre-commit check failed: mvtags
    echo "Pre-commit check failed - mvtags are present in the following files:"
    echo $RESULT
    # mvtodo: allow the commit to be interactively forced despite of this warning.
    return 1
  fi
  git commit $@
}

alias gista="git status"
alias giadd="git add"
alias giunadd="git reset HEAD"
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

