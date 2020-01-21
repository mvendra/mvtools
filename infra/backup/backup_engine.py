#!/usr/bin/env python3

import time
import datetime
import os
from subprocess import call
import shutil
import glob
import path_utils
import encrypt
import terminal_colors

import hash_algos
import create_and_write_file

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))

class BackupEngine:

    def __init__(_self, bkprep, bkarts, bktgs_root, bktgs_base, bktmp, pphrase):
        _self.BKPREPARATION = bkprep
        _self.BKARTIFACTS = bkarts
        _self.BKTARGETS_ROOT = bktgs_root
        _self.BKTARGETS_BASEDIR = bktgs_base
        _self.BKTEMP = bktmp
        _self.PASSPHRASE = pphrase

    def gettimestamp(_self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S %d-%m-%Y')

    def run(_self):

        # validations
        for it in _self.BKARTIFACTS:
            if not os.path.exists(it):
                print("%sThe path [%s] is marked for backing up, but does not exist. Aborting%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        if os.path.exists(_self.BKTEMP):
            print("%s[%s] already exists. For safety reasons, this script is aborted.%s" % (terminal_colors.TTY_RED, _self.BKTEMP, terminal_colors.TTY_WHITE))
            return False

        print("%sBeginning backup operations at %s.%s" % (terminal_colors.TTY_GREEN, _self.gettimestamp(), terminal_colors.TTY_WHITE))

        _self.EXCLUDEFOLDERS = []
        """
        The feature below has been deprecated in early 2015. I'd much rather separate exceptions in different base folders altogether, for simplicity.
        I'm leaving the code below just in case there's ever a need to revive it for whatever reason - on which case it should be reworked though.
        Instead of using a list, use a dict instead, to associate a base subfolder with its exceptions. Otherwise, every, say unwanted_folder_inside_Dev inside other folders
        would also always be ignored. This could cause side effects, so beware.
                for it in _self.BKARTIFACTS_EXCEPTIONS:
                    if not os.path.isdir(it):
                        print('The path %s is marked as a backup exception, but does not exist. Aborting.' % it)
                        sys.exit(1)
                    else:
                        _self.EXCLUDEFOLDERS.append("--exclude=%s" % it)
        """

        for it in _self.BKTARGETS_ROOT:
            if not os.path.isdir(it):
                print("%sThe path [%s] is marked as a writing target, but does not exist. Aborting.%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        if _self.BKPREPARATION != "":
            print("%sPreparing...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
            prep_r = call([_self.BKPREPARATION])
            if prep_r != 0:
                print("%sFailed preparing backup. Aborting.%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        print("%sDeleting old backup...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
        for it in _self.BKTARGETS_ROOT:
            test_subj = os.path.join(it, _self.BKTARGETS_BASEDIR)
            if not path_utils.scratchfolder(test_subj):
                print("%sCannot scratch %s - are the external media available/attached?%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        print("%sCreating backup...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

        path_utils.scratchfolder(_self.BKTEMP)
        with open(os.path.join(_self.BKTEMP, "bk_date.txt"), "w+") as f:
            f.write(_self.gettimestamp() + "\n")

        for it in _self.BKARTIFACTS:
            print("%sCurrent: %s, started at %s%s" % (terminal_colors.TTY_GREEN, it, datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'), terminal_colors.TTY_WHITE))
            BKTMP_PLUS_ARTBASE = os.path.join(_self.BKTEMP, os.path.basename(os.path.dirname(it)))
            path_utils.guaranteefolder(BKTMP_PLUS_ARTBASE)
            CURPAK = os.path.join(BKTMP_PLUS_ARTBASE, os.path.basename(it) + ".tar")
            tarcmd = ["tar"]
            for ef in _self.EXCLUDEFOLDERS:
                tarcmd.append(ef)
            tarcmd += ["-cf", CURPAK, it]
            call(tarcmd)
            call(["bzip2", CURPAK])
            CURPAK += ".bz2"
            encrypt.symmetric_encrypt(CURPAK, CURPAK + ".enc", _self.PASSPHRASE)
            os.unlink(CURPAK) # delete plain package
            CURPAK += ".enc"
            CURPAK_HASH_FILE = CURPAK + ".sha256"
            v, r = hash_algos.hash_sha_256_app_file(CURPAK)
            if not v:
                print("Failed generating hash for [%s]." % CURPAK)
                return False
            create_and_write_file.create_file_contents(CURPAK_HASH_FILE, r)

        print("%sWriting to targets...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

        for it in _self.BKTARGETS_ROOT:
            shutil.copy(os.path.join(_self.BKTEMP, "bk_date.txt"), os.path.join(it, _self.BKTARGETS_BASEDIR))
            for cur_art_base in os.listdir(_self.BKTEMP):
                for fn in glob.glob(os.path.join(_self.BKTEMP, cur_art_base, '*.*')):
                    final_target_folder = os.path.join(it, _self.BKTARGETS_BASEDIR, cur_art_base)
                    path_utils.guaranteefolder(final_target_folder)
                    shutil.copy(fn, final_target_folder)
            call(["umount", it])

        shutil.rmtree(_self.BKTEMP)
        print("%sDone at %s%s" % (terminal_colors.TTY_GREEN, _self.gettimestamp(), terminal_colors.TTY_WHITE))

        return True
