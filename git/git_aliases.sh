#!/bin/bash

# COMMIT
gicom(){

    len_inputs=0
    ignore_mvtags_switch=false
    use_editor=false

    for a in "$@"; do
        len_inputs=$((len_inputs+1))
        if [ "$a" == "--ignore-mvtags" ]; then
            ignore_mvtags_switch=true
        fi
    done

    if [ $len_inputs -eq 0 ]; then # no parameters. use commit with editor mode.
        use_editor=true
    elif [ $len_inputs -eq 1 ] && [ "$ignore_mvtags_switch" = true ]; then # only one parameter and it was the "--ignore-mvtags" ovveride switch. use commit with editor mode.
        use_editor=true
    fi

    if [ "$use_editor" = true ]; then

        if [ "$ignore_mvtags_switch" = false ]; then
            test_mvtags_in_git_cache.py
            if [ $? -ne 0 ]; then
                return 1
            fi
        fi
        git commit

    else
        git_commit_with_prechecks.py "$@"
    fi

}

alias gichepi="git cherry-pick"

# DIFF
alias gidif_setgui="git config --global diff.external meldiff.py"
alias gidif_setcmd="git config --global --unset diff.external"
alias gidif="git diff"
alias gidifsta="git diff --staged"
alias gidifca="git diff --cached"
alias gidif_noext="gidif --no-ext"

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
    # on this user's defined temp folder (MVTOOLS_TEMP_PATH)
    # will not run if there is no pre-existing temp folder
    # HEAD is patch-0, deepest ($1) commit
    # is patch-$1

    R=`git status -s`
    if [[ ! -z $R ]]; then
        echo "HEAD is not clear. Aborting."
        return
    fi

    TEMP_FOLDER="$MVTOOLS_TEMP_PATH"
    if [ ! -d $TEMP_FOLDER ]; then
        echo "No [$TEMP_FOLDER] (MVTOOLS_TEMP_PATH envvar) folder found. Aborting."
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

    # binary patches safety
    gisho --oneline | egrep "Binary files (.)* differ"
    if [ $? -eq 0 ]; then
        echo "The last commit was binary. The backup patch will be ineffective. Press any key to proceed."
        read
    fi

    # backs up all commits to be deleted
    MAX=$RANGE
    (( MAX-- ))
    for i in `seq 0 $MAX`; do
        HASH=`get_git_hash.py`
        FN="$TEMP_FOLDER/gikill_backup_"
        FN+=$HASH
        FN+="_"
        FN+="$i.patch"
        git show HEAD~$i > $FN
    done

    # carries out the removal
    git reset --hard HEAD~$RANGE

}

alias gista="git status"
alias giadd="git add"
alias giunadd="git reset HEAD" # mvtodo: does not work before the first commit
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
alias giconf="git config"
alias gireb="git rebase"
alias girem="git remote -v"
alias gigre="git grep -n"
alias gihel="git help"
alias gibla="git blame"
alias gistash="git stash"
alias giver="git version"
alias gicle="git clean"
alias gifsck="git fsck"
alias gilsu="git ls-files --exclude-standard --others"

alias gimv="git mv"
alias girm="git rm"
