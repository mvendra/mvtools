#!/usr/bin/env python3

import os
import time
import datetime
from subprocess import call
import shutil

import terminal_colors
import path_utils
import pakgen
import encrypt
import sha256_wrapper
import shred_wrapper
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

        for it in _self.BKTARGETS_ROOT:
            if not os.path.isdir(it):
                print("%sThe path [%s] is marked as a writing target, but does not exist. Aborting.%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        if len(_self.BKPREPARATION) == 2:
            if len(_self.BKPREPARATION[0]) > 0:
                print("%sPreparing...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
                prep_cmd = [_self.BKPREPARATION[0]]
                for prep_arg in _self.BKPREPARATION[1]:
                    prep_cmd.append(prep_arg)
                prep_r = call(prep_cmd)
                if prep_r != 0:
                    print("%sFailed preparing backup. Aborting.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
                    return False

        print("%sDeleting old backup...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
        for it in _self.BKTARGETS_ROOT:
            test_subj = path_utils.concat_path(it, _self.BKTARGETS_BASEDIR)
            if not path_utils.scratchfolder(test_subj):
                print("%sCannot scratch %s - are the external media available/attached?%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False
            else:
                shutil.rmtree(test_subj) # redundant but necessary

        print("%sCreating backup...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

        path_utils.scratchfolder(_self.BKTEMP)
        BKTEMP_AND_BASEDIR = path_utils.concat_path(_self.BKTEMP, _self.BKTARGETS_BASEDIR)
        os.mkdir(BKTEMP_AND_BASEDIR)
        with open(path_utils.concat_path(BKTEMP_AND_BASEDIR, "bk_date.txt"), "w+") as f:
            f.write(_self.gettimestamp() + "\n")

        for it in _self.BKARTIFACTS:
            print("%sCurrent: %s, started at %s%s" % (terminal_colors.TTY_GREEN, it, datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'), terminal_colors.TTY_WHITE))
            BKTMP_PLUS_ARTBASE = path_utils.concat_path(BKTEMP_AND_BASEDIR, os.path.basename(os.path.dirname(it)))
            path_utils.guaranteefolder(BKTMP_PLUS_ARTBASE)

            CURPAK = path_utils.concat_path(BKTMP_PLUS_ARTBASE, os.path.basename(it))
            CURPAK_TAR_BZ2 = CURPAK + ".tar.bz2"
            CURPAK_TAR_BZ2_ENC = CURPAK_TAR_BZ2 + ".enc"
            CURPAK_TAR_BZ2_ENC_HASH = CURPAK_TAR_BZ2_ENC + ".sha256"

            # create the package
            v = pakgen.pakgen(CURPAK, False, [it]) # hash will be generated later (from the encrypted package)
            if not v:
                print("Failed generating [%s]." % CURPAK_TAR_BZ2)
                return False

            # encrypt plain package
            v, r = encrypt.symmetric_encrypt(CURPAK_TAR_BZ2, CURPAK_TAR_BZ2_ENC, _self.PASSPHRASE)
            if not v:
                print("Failed encrypting package: %s." % r)
                return False

            # shred plain package
            v, r = shred_wrapper.shred_target(CURPAK_TAR_BZ2)
            if not v:
                print("Failed shredding plain package: %s." % r)
                return False

            # create hash from the encrypted package
            v, r = sha256_wrapper.hash_sha_256_app_file(CURPAK_TAR_BZ2_ENC)
            if not v:
                print("Failed generating hash for [%s]." % CURPAK_TAR_BZ2_ENC)
                return False
            create_and_write_file.create_file_contents(CURPAK_TAR_BZ2_ENC_HASH, r)

        print("%sWriting to targets...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

        for it in _self.BKTARGETS_ROOT:
            shutil.copytree(BKTEMP_AND_BASEDIR, path_utils.concat_path(it, _self.BKTARGETS_BASEDIR))
            call(["umount", it])

        shutil.rmtree(_self.BKTEMP)
        print("%sDone at %s%s" % (terminal_colors.TTY_GREEN, _self.gettimestamp(), terminal_colors.TTY_WHITE))

        return True
