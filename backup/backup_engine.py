#!/usr/bin/env python3

import os
import shutil

import path_utils
import generic_run
import pakgen
import encrypt
import dirsize
import sha256_wrapper
import shred_wrapper
import terminal_colors
import maketimestamp
import create_and_write_file

def _get_dirname_helper(path):
    dn = path_utils.dirname_filtered(path)
    if dn is None:
        _msg = "WARNING! Path [%s] was deduced to be inside root. It will be placed inside the '(root)' folder!" % path
        print("%s%s%s" % (terminal_colors.TTY_YELLOW_BOLD, _msg, terminal_colors.TTY_WHITE))
        return "(root)"
    return dn

class BackupEngine:

    def __init__(_self, bkprep, bkarts, bktgs_root, bktgs_base, bktmp, bkwarns, pphrase):
        _self.BKPREPARATION = bkprep
        _self.BKARTIFACTS = bkarts
        _self.BKTARGETS_ROOT = bktgs_root
        _self.BKTARGETS_BASEDIR = bktgs_base
        _self.BKTEMP = bktmp
        _self.BKWARNINGS = bkwarns
        _self.PASSPHRASE = pphrase

    def run(_self):

        dirname_sentinel = {}

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

        print("%sBeginning backup operations at %s.%s" % (terminal_colors.TTY_GREEN, maketimestamp.get_timestamp_now(), terminal_colors.TTY_WHITE))

        for it in _self.BKTARGETS_ROOT:
            if not os.path.isdir(it):
                print("%sThe path [%s] is marked as a writing target, but does not exist. Aborting.%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False

        if len(_self.BKPREPARATION) == 2:
            if len(_self.BKPREPARATION[0]) > 0:
                print("%sPreparing...%s" % (terminal_colors.TTY_BLUE, terminal_colors.TTY_WHITE))
                prep_cmd = [_self.BKPREPARATION[0]]
                for prep_arg in _self.BKPREPARATION[1]:
                    prep_cmd.append(prep_arg)
                prepv, prepr = generic_run.run_cmd_simple(prep_cmd)
                if not prepv:
                    print("%sFailed preparing backup: [%s]. Aborting.%s" % (terminal_colors.TTY_RED, prepr, terminal_colors.TTY_WHITE))
                    return False

        print("%sDeleting old backup...%s" % (terminal_colors.TTY_BLUE, terminal_colors.TTY_WHITE))
        for it in _self.BKTARGETS_ROOT:
            test_subj = path_utils.concat_path(it, _self.BKTARGETS_BASEDIR)
            if not path_utils.scratchfolder(test_subj):
                print("%sCannot scratch %s - are the external media available/attached?%s" % (terminal_colors.TTY_RED, it, terminal_colors.TTY_WHITE))
                return False
            else:
                shutil.rmtree(test_subj) # redundant but necessary

        print("%sCreating backup...%s" % (terminal_colors.TTY_BLUE, terminal_colors.TTY_WHITE))

        if not path_utils.scratchfolder(_self.BKTEMP):
            print("%sUnable to create temporary path [%s]. Aborting.%s" % (terminal_colors.TTY_RED, _self.BKTEMP, terminal_colors.TTY_WHITE))
            return False
        BKTEMP_AND_BASEDIR = path_utils.concat_path(_self.BKTEMP, _self.BKTARGETS_BASEDIR)
        os.mkdir(BKTEMP_AND_BASEDIR)
        if not os.path.exists(BKTEMP_AND_BASEDIR):
            print("%sUnable to create temporary+base path [%s]. Aborting.%s" % (terminal_colors.TTY_RED, BKTEMP_AND_BASEDIR, terminal_colors.TTY_WHITE))
            return False
        with open(path_utils.concat_path(BKTEMP_AND_BASEDIR, "bk_date.txt"), "w+") as f:
            f.write(maketimestamp.get_timestamp_now() + "\n")

        for it in _self.BKARTIFACTS:
            print("%sCurrent: %s, started at %s%s" % (terminal_colors.TTY_BLUE, it[0], maketimestamp.get_timestamp_now(), terminal_colors.TTY_WHITE))

            dn = _get_dirname_helper(it[0])
            bn_of_dn = path_utils.basename_filtered(dn)

            # check if this basename-of-dirname has already been used for another (albeit similar) full dirname
            if bn_of_dn in dirname_sentinel:
                if dirname_sentinel[bn_of_dn] != dn: # same basename-of-dirname but different dirname overall. issue a warning about risk of overwrites.
                    _msg = "WARNING! Path [%s] has a common dirname with another artifact (%s). Both artifacts will be placed inside the same folder in the target backup base folder!" % (it[0], dirname_sentinel[bn_of_dn])
                    print("%s%s%s" % (terminal_colors.TTY_YELLOW_BOLD, _msg, terminal_colors.TTY_WHITE))
            else:
                dirname_sentinel[bn_of_dn] = dn

            BKTMP_PLUS_ARTBASE = path_utils.concat_path(BKTEMP_AND_BASEDIR, bn_of_dn)
            if path_utils.basename_filtered(BKTMP_PLUS_ARTBASE) == path_utils.basename_filtered(BKTEMP_AND_BASEDIR):
                _msg = "WARNING! Path [%s] was deduced to be inside root. It will be placed inside the '(root)' folder!" % it[0]
                print("%s%s%s" % (terminal_colors.TTY_YELLOW_BOLD, _msg, terminal_colors.TTY_WHITE))
                BKTMP_PLUS_ARTBASE = path_utils.concat_path(BKTMP_PLUS_ARTBASE, "(root)")
            path_utils.guaranteefolder(BKTMP_PLUS_ARTBASE)

            CURPAK = path_utils.concat_path(BKTMP_PLUS_ARTBASE, path_utils.basename_filtered(it[0]))
            CURPAK_TAR = CURPAK + ".tar"
            CURPAK_TAR_BZ2 = CURPAK_TAR + ".bz2"
            CURPAK_TAR_BZ2_ENC = CURPAK_TAR_BZ2 + ".enc"
            CURPAK_TAR_BZ2_ENC_HASH = CURPAK_TAR_BZ2_ENC + ".sha256"

            # check if there are any preexisting artifacts
            if os.path.exists(CURPAK):
                print("%sFailed generating [%s] - duplicated artifact - aborting to avoid overwrites.%s" % (terminal_colors.TTY_RED, CURPAK, terminal_colors.TTY_WHITE))
                return False
            if os.path.exists(CURPAK_TAR):
                print("%sFailed generating [%s] - duplicated artifact - aborting to avoid overwrites.%s" % (terminal_colors.TTY_RED, CURPAK_TAR, terminal_colors.TTY_WHITE))
                return False
            if os.path.exists(CURPAK_TAR_BZ2):
                print("%sFailed generating [%s] - duplicated artifact - aborting to avoid overwrites.%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2, terminal_colors.TTY_WHITE))
                return False
            if os.path.exists(CURPAK_TAR_BZ2_ENC):
                print("%sFailed generating [%s] - duplicated artifact - aborting to avoid overwrites.%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2_ENC, terminal_colors.TTY_WHITE))
                return False
            if os.path.exists(CURPAK_TAR_BZ2_ENC_HASH):
                print("%sFailed generating [%s] - duplicated artifact - aborting to avoid overwrites.%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2_ENC_HASH, terminal_colors.TTY_WHITE))
                return False

            # create the package
            v, r = pakgen.pakgen(CURPAK, False, [it[0]]) # hash will be generated later (from the encrypted package)
            if not v:
                print("%sFailed generating [%s].%s" % (terminal_colors.TTY_RED, CURPAK_TAR_BZ2, terminal_colors.TTY_WHITE))
                return False
            if len(r) > 0:
                print("Output from pakgen: %s" % r)

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

        print("%sWriting to targets...%s" % (terminal_colors.TTY_BLUE, terminal_colors.TTY_WHITE))

        for it in _self.BKTARGETS_ROOT:
            shutil.copytree(BKTEMP_AND_BASEDIR, path_utils.concat_path(it, _self.BKTARGETS_BASEDIR))
            generic_run.run_cmd_simple(["umount", it])

        shutil.rmtree(_self.BKTEMP)
        print("%sDone at %s%s" % (terminal_colors.TTY_GREEN, maketimestamp.get_timestamp_now(), terminal_colors.TTY_WHITE))

        return True
