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
import dirsize
import sha256_wrapper
import shred_wrapper
import create_and_write_file

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))

class BackupEngine:

    def __init__(_self, bkprep, bkarts, bktgs_root, bktgs_base, bktmp, bkwarns, pphrase):
        _self.BKPREPARATION = bkprep
        _self.BKARTIFACTS = bkarts
        _self.BKTARGETS_ROOT = bktgs_root
        _self.BKTARGETS_BASEDIR = bktgs_base
        _self.BKTEMP = bktmp
        _self.BKWARNINGS = bkwarns
        _self.PASSPHRASE = pphrase

    def gettimestamp(_self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S %d-%m-%Y')

    def run(_self):

        # validations
        art_filtered = []
        for it in _self.BKARTIFACTS:
            if not os.path.exists(it[0]):
                if it[1]:
                    print("%sThe path [%s] is marked for backing up, but does not exist. Aborting%s" % (terminal_colors.TTY_RED, it[0], terminal_colors.TTY_WHITE))
                    return False
                else:
                    print("%sThe path [%s] is marked for backing up, but does not exist.%s" % (terminal_colors.TTY_YELLOW_BOLD, it[0], terminal_colors.TTY_WHITE))
            else:
                art_filtered.append(it)
        _self.BKARTIFACTS = art_filtered

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
            print("%sCurrent: %s, started at %s%s" % (terminal_colors.TTY_GREEN, it[0], datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'), terminal_colors.TTY_WHITE))
            BKTMP_PLUS_ARTBASE = path_utils.concat_path(BKTEMP_AND_BASEDIR, path_utils.basename_filtered(os.path.dirname(it[0])))
            path_utils.guaranteefolder(BKTMP_PLUS_ARTBASE)

            CURPAK = path_utils.concat_path(BKTMP_PLUS_ARTBASE, path_utils.basename_filtered(it[0]))
            CURPAK_TAR_BZ2 = CURPAK + ".tar.bz2"
            CURPAK_TAR_BZ2_ENC = CURPAK_TAR_BZ2 + ".enc"
            CURPAK_TAR_BZ2_ENC_HASH = CURPAK_TAR_BZ2_ENC + ".sha256"

            # create the package
            v = pakgen.pakgen(CURPAK, False, [it[0]]) # hash will be generated later (from the encrypted package)
            if not v:
                print("%sFailed generating [%s].%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2, terminal_colors.TTY_WHITE))
                return False

            # encrypt plain package
            v, r = encrypt.symmetric_encrypt(CURPAK_TAR_BZ2, CURPAK_TAR_BZ2_ENC, _self.PASSPHRASE)
            if not v:
                print("%sFailed encrypting package: [%s].%s" % (terminal_colors.TTY_RED, r, terminal_colors.TTY_WHITE))
                return False

            # shred plain package
            v, r = shred_wrapper.shred_target(CURPAK_TAR_BZ2)
            if not v:
                print("%sFailed shredding plain package: [%s].%s" % (terminal_colors.TTY_RED, r, terminal_colors.TTY_WHITE))
                return False

            warn_size_each_active_local = (_self.BKWARNINGS[0][0] is not None) and (_self.BKWARNINGS[0][1] is not None)
            warn_size_each_local = _self.BKWARNINGS[0][0]
            warn_size_each_abort_local = _self.BKWARNINGS[0][1]

            if it[2] is not None:
                # warning size option overridden
                warn_size_each_active_local = True
                warn_size_each_local = it[2]

            if it[3] is not None:
                # warning abort option overridden
                warn_size_each_active_local = True
                warn_size_each_abort_local = it[3]

            if warn_size_each_active_local:
                if dirsize.get_dir_size(CURPAK_TAR_BZ2_ENC, False) > warn_size_each_local:
                    if warn_size_each_abort_local:
                        print("%sGenerated package [%s] exceeds the size limit. Aborting.%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2_ENC, terminal_colors.TTY_WHITE))
                        return False
                    else:
                        print("%sGenerated package [%s] exceeds the size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, CURPAK_TAR_BZ2_ENC, terminal_colors.TTY_WHITE))

            # create hash from the encrypted package
            v, r = sha256_wrapper.hash_sha_256_app_file(CURPAK_TAR_BZ2_ENC)
            if not v:
                print("%sFailed generating hash for [%s].%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2_ENC, terminal_colors.TTY_WHITE))
                return False
            create_and_write_file.create_file_contents(CURPAK_TAR_BZ2_ENC_HASH, r)

        warn_size_final_active_local = (_self.BKWARNINGS[1][0] is not None) and (_self.BKWARNINGS[1][1] is not None)
        if warn_size_final_active_local:
            if dirsize.get_dir_size(BKTEMP_AND_BASEDIR, False) > _self.BKWARNINGS[1][0]:
                if _self.BKWARNINGS[1][1]: # abort
                    print("%sGenerated backup exceeds size limit. Aborting.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
                    return False
                else:
                    print("%sGenerated backup exceeds size limit.%s" % (terminal_colors.TTY_YELLOW_BOLD, terminal_colors.TTY_WHITE))

        print("%sWriting to targets...%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

        for it in _self.BKTARGETS_ROOT:
            shutil.copytree(BKTEMP_AND_BASEDIR, path_utils.concat_path(it, _self.BKTARGETS_BASEDIR))
            call(["umount", it])

        shutil.rmtree(_self.BKTEMP)
        print("%sDone at %s%s" % (terminal_colors.TTY_GREEN, _self.gettimestamp(), terminal_colors.TTY_WHITE))

        return True
