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

  # removes $1 commits from the repository
  # saves a backup of each commit as a patch
  # on this user's nuke folder ($HOME/nuke)
  # will not run if there is no nuke folder
  # HEAD is patch-0, deepest ($1) commit
  # is patch-$1

  R=`git status -s`
  if [[ ! -z $R ]]; then
    echo "HEAD is not clear. Aborting."
    return
  fi

  NUKE="$HOME/nuke"
  if [ ! -d $NUKE ]; then
    echo "No $NUKE folder found. Aborting."
    return
  fi

  NUM_COMMITS=`git log --oneline | wc -l`

  RANGE=$1
  if [ -z $1 ]; then
    RANGE=1
  fi

  #if ((RANGE > NUM_COMMITS)); then
  if [ "$RANGE" -gt "$NUM_COMMITS" ]; then
    echo "Requested deletion of more commits than there are. Aborting."
    return
  fi

  # backs up all commits to be deleted
  MAX=$RANGE
  (( MAX-- ))
  for i in `seq 0 $MAX`; do
    FN="$NUKE/gikill_backup_$i.patch"
    git show HEAD~$i > $FN
  done

  # carries out the removal
  git reset --hard HEAD~$RANGE

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

