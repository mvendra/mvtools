#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import create_and_write_file
import mvtools_test_fixture

import hash_check
import decrypt
import tar_wrapper
import path_utils
import convert_unit
import mvtools_envvars

import backup_processor

def get_tuple_list_index(the_tuple_list, the_key):
    for i in range(len(the_tuple_list)):
        if the_tuple_list[i][0] == the_key:
            return i
    return None

def escape(thestr):

    result = ""

    for i in thestr:
        if i == "\"" or i == "\\":
            result += "\\"
        result += i

    return result

class BackupProcessorTest(unittest.TestCase):

    def setUp(self):
        self.mvtools_envvars_inst = mvtools_envvars.Mvtools_Envvars()
        v, r = self.mvtools_envvars_inst.make_copy_environ()
        if not v:
            self.tearDown()
            self.fail(r)
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("backup_processor_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        v, r = mvtools_envvars.mvtools_envvar_read_test_bkproc_reserved_1()
        if v:
            return False, "Mvtool's backup_processor's test envvar is in use. This test requires it to not be in use."
        self.reserved_test_env_var = "$MVTOOLS_BKPROC_TEST_RESERVED_1"

        # folder where extracted stuff will be stored at
        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        path_utils.scratchfolder(self.extracted_folder)

        # nonexistent folder - for testing only
        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        # temp folder
        self.bk_test_temp_folder = path_utils.concat_path(self.test_dir, "bktemp")
        self.bk_test_temp_folder_space_1 = path_utils.concat_path(self.test_dir, "   bktemp")
        self.bk_test_temp_folder_space_2 = path_utils.concat_path(self.test_dir, "bk temp")
        self.bk_test_temp_folder_space_3 = path_utils.concat_path(self.test_dir, "bktemp   ")
        self.bk_test_temp_folder_nonexistent = path_utils.concat_path(self.test_dir, "nonexistent", "secondlevel")

        # base backup folder
        self.bk_base_folder_test = "BackupTests"
        self.bk_base_folder_test_space_1 = "   BackupTests"
        self.bk_base_folder_test_space_2 = "Backup   Tests"
        self.bk_base_folder_test_space_3 = "BackupTests   "

        # warning thresholds
        self.warn_each_1 = "8Gb"
        self.warn_final_1 = "240Gb"
        self.warn_each_2 = "4Mb"
        self.warn_final_2 = "120Mb"
        self.warn_each_3 = "4"
        self.warn_final_3 = "8"

        # create folders, source and target
        self.test_source_folder = path_utils.concat_path(self.test_dir, "source_test")
        os.mkdir(self.test_source_folder)
        self.test_source_alt_folder = path_utils.concat_path(self.test_dir, "source_alt_test")
        os.mkdir(self.test_source_alt_folder)
        self.test_source_folder_another = path_utils.concat_path(self.test_dir, "source_test_another")
        os.mkdir(self.test_source_folder_another)

        self.test_target_1_folder = path_utils.concat_path(self.test_dir, "target_1_test")
        os.mkdir(self.test_target_1_folder)
        self.test_target_2_folder = path_utils.concat_path(self.test_dir, "target_2_test")
        os.mkdir(self.test_target_2_folder)
        self.test_target_space_1_folder = path_utils.concat_path(self.test_dir, "   target_space_1_test")
        os.mkdir(self.test_target_space_1_folder)
        self.test_target_space_2_folder = path_utils.concat_path(self.test_dir, "target  space  2_test")
        os.mkdir(self.test_target_space_2_folder)
        self.test_target_space_3_folder = path_utils.concat_path(self.test_dir, "target_space_3_test   ")
        os.mkdir(self.test_target_space_3_folder)

        # create test folders
        self.folder1 = path_utils.concat_path(self.test_source_folder, "folder1")
        self.folder2 = path_utils.concat_path(self.test_source_folder, "folder2")
        self.folder3 = path_utils.concat_path(self.test_source_folder, "folder3")
        self.folder4 = path_utils.concat_path(self.test_source_folder, ".folder4")
        self.alt_folder5 = path_utils.concat_path(self.test_source_alt_folder, "folder5")
        self.alt_folder6 = path_utils.concat_path(self.test_source_alt_folder, "folder6")
        self.another_folder7 = path_utils.concat_path(self.test_source_folder_another, "folder7")
        os.mkdir(self.folder1)
        os.mkdir(self.folder2)
        os.mkdir(self.folder3)
        os.mkdir(self.folder4)
        os.mkdir(self.alt_folder5)
        os.mkdir(self.alt_folder6)
        os.mkdir(self.another_folder7)

        # file "zero" - at the root of the source dir
        self.file0 = path_utils.concat_path(self.test_source_folder, ".file0.txt")
        create_and_write_file.create_file_contents(self.file0, "xyz")

        # create subfolders
        self.folder1_subfolder1 = path_utils.concat_path(self.folder1, "subfolder1")
        os.mkdir(self.folder1_subfolder1)
        self.folder1_subfolder2 = path_utils.concat_path(self.folder1, "subfolder2")
        os.mkdir(self.folder1_subfolder2)

        # create files, folder1
        self.folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")
        self.folder1_subfolder1_file2 = path_utils.concat_path(self.folder1_subfolder1, "file2.txt")
        create_and_write_file.create_file_contents(self.folder1_subfolder1_file2, "abc")
        self.folder1_subfolder2_file3 = path_utils.concat_path(self.folder1_subfolder2, "file3.txt")
        create_and_write_file.create_file_contents(self.folder1_subfolder2_file3, "abc")

        # create files, folder2
        self.folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        # create files, folder3
        self.folder3_file1 = path_utils.concat_path(self.folder3, "file1.txt")
        create_and_write_file.create_file_contents(self.folder3_file1, "abc")

        # create files, folder4
        self.folder4_file1 = path_utils.concat_path(self.folder4, "file1.txt")
        create_and_write_file.create_file_contents(self.folder4_file1, "abc")

        # create files alt source folders
        self.alt_folder5_file1 = path_utils.concat_path(self.alt_folder5, "file51.txt")
        create_and_write_file.create_file_contents(self.alt_folder5_file1, "abc")
        self.alt_folder6_file1 = path_utils.concat_path(self.alt_folder6, "file61.txt")
        create_and_write_file.create_file_contents(self.alt_folder6_file1, "abc")
        self.file01 = path_utils.concat_path(self.test_source_alt_folder, ".file01.txt")
        create_and_write_file.create_file_contents(self.file01, "ooo")

        # create files another source folders
        self.file_another = path_utils.concat_path(self.another_folder7, "file_another.txt")
        create_and_write_file.create_file_contents(self.file_another, "zzz")

        # sources with spaces
        self.special_folder = path_utils.concat_path(self.test_source_folder, "special_folder")
        os.mkdir(self.special_folder)

        self.space_file1 = path_utils.concat_path(self.special_folder, "   sp_file1.txt")
        self.space_file2 = path_utils.concat_path(self.special_folder, "sp_fi  le2.txt")
        self.space_file3 = path_utils.concat_path(self.special_folder, "sp_file3.txt  ")
        self.quote_file1 = path_utils.concat_path(self.special_folder, "file\"1.txt")
        create_and_write_file.create_file_contents(self.space_file1, "eee1")
        create_and_write_file.create_file_contents(self.space_file2, "eee2")
        create_and_write_file.create_file_contents(self.space_file3, "eee3")
        create_and_write_file.create_file_contents(self.quote_file1, "eee4")

        self.space_folder1 = path_utils.concat_path(self.special_folder, "   sp_folder1")
        self.space_folder2 = path_utils.concat_path(self.special_folder, "sp_fol   der2")
        self.space_folder3 = path_utils.concat_path(self.special_folder, "sp_folder3   ")
        os.mkdir(self.space_folder1)
        os.mkdir(self.space_folder2)
        os.mkdir(self.space_folder3)

        # prep script - does not expect parameters, variations in the filenames
        self.prep_filename = path_utils.concat_path(self.test_dir, "preptest.py")
        self.prep_filename_space_1 = path_utils.concat_path(self.test_dir, "prep test.py")
        self.prep_filename_space_2 = path_utils.concat_path(self.test_dir, "  preptest.py")
        self.prep_filename_space_3 = path_utils.concat_path(self.test_dir, "preptest.py  ")
        self.prep_generated_test_filename = path_utils.concat_path(self.test_dir, "preptest_generated.txt")
        prep_file_contents = "#!/usr/bin/env python3" + os.linesep + os.linesep
        prep_file_contents += "import create_and_write_file" + os.linesep + os.linesep
        prep_file_contents += "if __name__ == \"__main__\":" + os.linesep
        prep_file_contents += "    contents = \"test\"" + os.linesep
        prep_file_contents += ("    filename = \"%s\"" + os.linesep) % self.prep_generated_test_filename
        prep_file_contents += "    create_and_write_file.create_file_contents(filename, contents)" + os.linesep
        create_and_write_file.create_file_contents(self.prep_filename, prep_file_contents)
        create_and_write_file.create_file_contents(self.prep_filename_space_1, prep_file_contents)
        create_and_write_file.create_file_contents(self.prep_filename_space_2, prep_file_contents)
        create_and_write_file.create_file_contents(self.prep_filename_space_3, prep_file_contents)
        os.chmod(self.prep_filename, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)
        os.chmod(self.prep_filename_space_1, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)
        os.chmod(self.prep_filename_space_2, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)
        os.chmod(self.prep_filename_space_3, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

        # prep script - expects parameters
        self.prep_param_filename = path_utils.concat_path(self.test_dir, "preptest_expects_params.py")
        self.prep_generated_param_test_filename = path_utils.concat_path(self.test_dir, "preptest_generated_param.txt")
        self.prep_generated_param_test_content = "generated content"
        prep_param_file_contents = "#!/usr/bin/env python3" + os.linesep + os.linesep
        prep_param_file_contents += "import sys" + os.linesep
        prep_param_file_contents += "import create_and_write_file" + os.linesep + os.linesep
        prep_param_file_contents += "if __name__ == \"__main__\":" + os.linesep
        prep_param_file_contents += "    if len(sys.argv) < 3:" + os.linesep
        prep_param_file_contents += "        sys.exit(1)" + os.linesep
        prep_param_file_contents += "    filename = sys.argv[1]" + os.linesep
        prep_param_file_contents += "    contents = sys.argv[2]" + os.linesep
        prep_param_file_contents += "    create_and_write_file.create_file_contents(filename, contents)" + os.linesep
        create_and_write_file.create_file_contents(self.prep_param_filename, prep_param_file_contents)
        os.chmod(self.prep_param_filename, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

        # prep script that fails
        self.prep_filename_fail = path_utils.concat_path(self.test_dir, "preptest_fail.py")
        self.prep_file_contents_fail = "#!/usr/bin/env python3" + os.linesep + os.linesep
        self.prep_file_contents_fail += "import sys" + os.linesep + os.linesep
        self.prep_file_contents_fail += "if __name__ == \"__main__\":" + os.linesep
        self.prep_file_contents_fail += "    sys.exit(1)" + os.linesep
        create_and_write_file.create_file_contents(self.prep_filename_fail, self.prep_file_contents_fail)
        os.chmod(self.prep_filename_fail, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

        # create (vanilla) config file
        self.cfg_file_contents = ""
        self.cfg_file_contents += ("BKPREPARATION = \"%s\"" + os.linesep) % (self.prep_filename)
        self.cfg_file_contents += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_1)
        self.cfg_file_contents += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_1)
        self.cfg_file_contents += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        self.cfg_file_contents += ("BKSOURCE {descend / ex: \"%s\" / ex: \"%s\"} = \"%s\"" + os.linesep) % (".file01.txt", "folder5", self.test_source_alt_folder)
        self.cfg_file_contents += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder_another
        self.cfg_file_contents += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        self.cfg_file_contents += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_2_folder
        self.cfg_file_contents += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        self.cfg_file_contents += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file = path_utils.concat_path(self.test_dir, "test_config_file.t20")
        create_and_write_file.create_file_contents(self.test_config_file, self.cfg_file_contents)

        # hash file
        self.hash_file = path_utils.concat_path(self.test_dir, ".hash_file_test")
        self.passphrase = "abcdef"
        create_and_write_file.create_file_contents(self.hash_file, "e32ef19623e8ed9d267f657a81944b3d07adbb768518068e88435745564e8d4150a0a703be2a7d88b61e3d390c2bb97e2d4c311fdc69d6b1267f05f59aa920e7")

        cfg_file_bktemp_nonexistent_contents = ""
        cfg_file_bktemp_nonexistent_contents += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_bktemp_nonexistent_contents += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_bktemp_nonexistent_contents += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder_nonexistent
        cfg_file_bktemp_nonexistent_contents += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_bktemp_nonexistent_file = path_utils.concat_path(self.test_dir, "test_config_bktemp_nonexistent_file.t20")
        create_and_write_file.create_file_contents(self.test_config_bktemp_nonexistent_file, cfg_file_bktemp_nonexistent_contents)

        # special source, 1
        special_source_cfg_file_contents1 = ""
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_file1
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_file2
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_file3
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % escape(self.quote_file1)
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_folder1
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_folder2
        special_source_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.space_folder3
        special_source_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        special_source_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_2_folder
        special_source_cfg_file_contents1 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        special_source_cfg_file_contents1 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_special_source_config_file = path_utils.concat_path(self.test_dir, "test_special_source_config_file.t20")
        create_and_write_file.create_file_contents(self.test_special_source_config_file, special_source_cfg_file_contents1)

        # special targets, 1
        special_target_cfg_file_contents1 = ""
        special_target_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        special_target_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_space_1_folder
        special_target_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_space_2_folder
        special_target_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_space_3_folder
        special_target_cfg_file_contents1 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        special_target_cfg_file_contents1 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_special_target_config_file = path_utils.concat_path(self.test_dir, "test_special_target_config_file.t20")
        create_and_write_file.create_file_contents(self.test_special_target_config_file, special_target_cfg_file_contents1)

        # special bk base and temp folders, 1
        special_base_and_tmp_cfg_file_contents1 = ""
        special_base_and_tmp_cfg_file_contents1 += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        special_base_and_tmp_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        special_base_and_tmp_cfg_file_contents1 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder_space_1
        special_base_and_tmp_cfg_file_contents1 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test_space_1
        self.test_special_base_and_temp_config_file1 = path_utils.concat_path(self.test_dir, "test_special_base_and_temp_config_file1.t20")
        create_and_write_file.create_file_contents(self.test_special_base_and_temp_config_file1, special_base_and_tmp_cfg_file_contents1)

        special_base_and_tmp_cfg_file_contents2 = ""
        special_base_and_tmp_cfg_file_contents2 += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        special_base_and_tmp_cfg_file_contents2 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        special_base_and_tmp_cfg_file_contents2 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder_space_2
        special_base_and_tmp_cfg_file_contents2 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test_space_2
        self.test_special_base_and_temp_config_file2 = path_utils.concat_path(self.test_dir, "test_special_base_and_temp_config_file2.t20")
        create_and_write_file.create_file_contents(self.test_special_base_and_temp_config_file2, special_base_and_tmp_cfg_file_contents2)

        special_base_and_tmp_cfg_file_contents3 = ""
        special_base_and_tmp_cfg_file_contents3 += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        special_base_and_tmp_cfg_file_contents3 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        special_base_and_tmp_cfg_file_contents3 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder_space_3
        special_base_and_tmp_cfg_file_contents3 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test_space_3
        self.test_special_base_and_temp_config_file3 = path_utils.concat_path(self.test_dir, "test_special_base_and_temp_config_file3.t20")
        create_and_write_file.create_file_contents(self.test_special_base_and_temp_config_file3, special_base_and_tmp_cfg_file_contents3)

        # malformed cfg file 1
        malformed_cfg_file_contents1 = ""
        malformed_cfg_file_contents1 = ("BKSORUCE = \"%s\"" + os.linesep) % self.space_file1
        malformed_cfg_file_contents1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        malformed_cfg_file_contents1 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        malformed_cfg_file_contents1 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_malformed_config_file1 = path_utils.concat_path(self.test_dir, "test_malformed_config_file1.t20")
        create_and_write_file.create_file_contents(self.test_malformed_config_file1, malformed_cfg_file_contents1)

        # malformed cfg file 2
        malformed_cfg_file_contents2 = ""
        malformed_cfg_file_contents2 = ("BKSOURCE = \"%s\"" + os.linesep) % self.space_file1
        #malformed_cfg_file_contents2 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\" + os.linesep)" % self.test_target_1_folder
        malformed_cfg_file_contents2 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        malformed_cfg_file_contents2 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_malformed_config_file2 = path_utils.concat_path(self.test_dir, "test_malformed_config_file2.t20")
        create_and_write_file.create_file_contents(self.test_malformed_config_file2, malformed_cfg_file_contents2)

        # malformed cfg file 3
        malformed_cfg_file_contents3 = ""
        malformed_cfg_file_contents3 = ("BKSOURCE = %s\"" + os.linesep) % self.space_file1
        malformed_cfg_file_contents3 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        malformed_cfg_file_contents3 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        malformed_cfg_file_contents3 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_malformed_config_file3 = path_utils.concat_path(self.test_dir, "test_malformed_config_file3.t20")
        create_and_write_file.create_file_contents(self.test_malformed_config_file3, malformed_cfg_file_contents3)

        # config file, with BKPREPARATION pointing to values (paths with spaces) 1
        cfg_file_contents_prep_space_1 = ""
        cfg_file_contents_prep_space_1 += ("BKPREPARATION = \"%s\"" + os.linesep) % self.prep_filename_space_1
        cfg_file_contents_prep_space_1 += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_prep_space_1 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_prep_space_1 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_prep_space_1 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.cfg_file_prep_space_1 = path_utils.concat_path(self.test_dir, "config_file_prep_space_1.t20")
        create_and_write_file.create_file_contents(self.cfg_file_prep_space_1, cfg_file_contents_prep_space_1)

        # config file, with BKPREPARATION pointing to values (paths with spaces) 2
        cfg_file_contents_prep_space_2 = ""
        cfg_file_contents_prep_space_2 += ("BKPREPARATION = \"%s\"" + os.linesep) % self.prep_filename_space_2
        cfg_file_contents_prep_space_2 += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_prep_space_2 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_prep_space_2 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_prep_space_2 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.cfg_file_prep_space_2 = path_utils.concat_path(self.test_dir, "config_file_prep_space_2.t20")
        create_and_write_file.create_file_contents(self.cfg_file_prep_space_2, cfg_file_contents_prep_space_2)

        # config file, with BKPREPARATION pointing to values (paths with spaces) 3
        cfg_file_contents_prep_space_3 = ""
        cfg_file_contents_prep_space_3 += ("BKPREPARATION = \"%s\"" + os.linesep) % self.prep_filename_space_3
        cfg_file_contents_prep_space_3 += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_prep_space_3 += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_prep_space_3 += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_prep_space_3 += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.cfg_file_prep_space_3 = path_utils.concat_path(self.test_dir, "config_file_prep_space_3.t20")
        create_and_write_file.create_file_contents(self.cfg_file_prep_space_3, cfg_file_contents_prep_space_3)

        # config file, with BKPREPARATION pointing to a script that fails
        cfg_file_contents_prep_fails = ""
        cfg_file_contents_prep_fails += ("BKPREPARATION = \"%s\"" + os.linesep) % self.prep_filename_fail
        cfg_file_contents_prep_fails += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_prep_fails += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_prep_fails += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_prep_fails += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.cfg_file_prep_fails = path_utils.concat_path(self.test_dir, "config_file_prep_fails.t20")
        create_and_write_file.create_file_contents(self.cfg_file_prep_fails, cfg_file_contents_prep_fails)

        # config file, BKPREPARATION that receives params, specified with an envvar
        cfg_file_contents_prep_param = ""
        cfg_file_contents_prep_param += ("BKPREPARATION {param: \"%s\" / param: \"%s\"} = \"%s\"" + os.linesep) % (self.reserved_test_env_var, self.prep_generated_param_test_content, self.prep_param_filename)
        cfg_file_contents_prep_param += ("BKWARNING_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_each_2)
        cfg_file_contents_prep_param += ("BKWARNING_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_final_2)
        cfg_file_contents_prep_param += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_prep_param += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_prep_param += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_prep_param += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_prep_param = path_utils.concat_path(self.test_dir, "test_config_file_prep_param.t20")
        create_and_write_file.create_file_contents(self.test_config_file_prep_param, cfg_file_contents_prep_param)

        # config file with a nonaborting nonexistent source
        cfg_file_contents_noabort_nonexistent = ""
        cfg_file_contents_noabort_nonexistent += ("BKSOURCE = \"%s\"" + os.linesep) % self.nonexistent
        cfg_file_contents_noabort_nonexistent += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        cfg_file_contents_noabort_nonexistent += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_noabort_nonexistent += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_noabort_nonexistent += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_noabort_nonexistent = path_utils.concat_path(self.test_dir, "test_config_file_noabort_nonexistent.t20")
        create_and_write_file.create_file_contents(self.test_config_file_noabort_nonexistent, cfg_file_contents_noabort_nonexistent)

        # config file with an aborting nonexistent source
        cfg_file_contents_abort_nonexistent = ""
        cfg_file_contents_abort_nonexistent += ("BKSOURCE {abort} = \"%s\"" + os.linesep) % self.nonexistent
        cfg_file_contents_abort_nonexistent += ("BKSOURCE = \"%s\"" + os.linesep) % self.folder1
        cfg_file_contents_abort_nonexistent += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_abort_nonexistent += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_abort_nonexistent += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_abort_nonexistent = path_utils.concat_path(self.test_dir, "test_config_file_abort_nonexistent.t20")
        create_and_write_file.create_file_contents(self.test_config_file_abort_nonexistent, cfg_file_contents_abort_nonexistent)

        # config file, global warnings (each/final) that do not cause aborts
        cfg_file_contents_warn_global_each_final_noabort = ""
        cfg_file_contents_warn_global_each_final_noabort += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_3)
        cfg_file_contents_warn_global_each_final_noabort += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_3)
        cfg_file_contents_warn_global_each_final_noabort += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_warn_global_each_final_noabort += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_noabort += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_noabort += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_noabort = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_noabort.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_noabort, cfg_file_contents_warn_global_each_final_noabort)

        # config file, global warnings (each) that do cause aborts
        cfg_file_contents_warn_global_each_abort = ""
        cfg_file_contents_warn_global_each_abort += ("BKWARNING_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_each_3)
        cfg_file_contents_warn_global_each_abort += ("BKWARNING_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_abort += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_warn_global_each_abort += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_abort += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_abort += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_abort = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_abort.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_abort, cfg_file_contents_warn_global_each_abort)

        # config file, global warnings (final) that do cause aborts
        cfg_file_contents_warn_global_final_abort = ""
        cfg_file_contents_warn_global_final_abort += ("BKWARNING_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_final_abort += ("BKWARNING_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_final_3)
        cfg_file_contents_warn_global_final_abort += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_warn_global_final_abort += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_final_abort += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_final_abort += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_final_abort = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_final_abort.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_final_abort, cfg_file_contents_warn_global_final_abort)

        # config file, global warnings (each/final), no aborts, each overridden
        cfg_file_contents_warn_global_each_final_noabort_each_overridden = ""
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKSOURCE {warn_size: \"%s\"} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_folder)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_noabort_each_overridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_noabort_each_overridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_noabort_each_overridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_noabort_each_overridden, cfg_file_contents_warn_global_each_final_noabort_each_overridden)

        # config file, global warnings (each/final), no aborts, each overridden + abort overridden
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden = ""
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKSOURCE {warn_size: \"%s\" / warn_abort} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_folder)
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_noabort_each_overridden_abortoverridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_noabort_each_overridden_abortoverridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_noabort_each_overridden_abortoverridden, cfg_file_contents_warn_global_each_final_noabort_each_overridden_abortoverridden)

        # config file, global warnings (each/final), each aborts, each overridden
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden = ""
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKWARNING_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKSOURCE {warn_size: \"%s\"} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_folder)
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_eachabort_each_overridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_eachabort_each_overridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_eachabort_each_overridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_eachabort_each_overridden, cfg_file_contents_warn_global_each_final_eachabort_each_overridden)

        # config file, global warnings (each/final), final aborts, each overridden
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden = ""
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKWARNING_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKSOURCE {warn_size: \"%s\"} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_folder)
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_finalabort_each_overridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_finalabort_each_overridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_finalabort_each_overridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_finalabort_each_overridden, cfg_file_contents_warn_global_each_final_finalabort_each_overridden)

        # config file, global warnings (each/final), final aborts, two eachs, one each overridden, the other left original
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden = ""
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKWARNING_EACH = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKWARNING_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKSOURCE {warn_size: \"%s\"} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_alt_folder)
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_finalabort_twoeachs_oneoverridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_finalabort_twoeachs_oneoverridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_finalabort_twoeachs_oneoverridden, cfg_file_contents_warn_global_each_final_finalabort_twoeachs_oneoverridden)

        # config file, global warnings (each/final), each aborts, two eachs, one each overridden, the other left original
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden = ""
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKWARNING_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_each_1)
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKWARNING_FINAL = \"%s\"" + os.linesep) % (self.warn_final_1)
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKSOURCE = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKSOURCE {warn_size: \"%s\"} = \"%s\"" + os.linesep) % (self.warn_each_3, self.test_source_alt_folder)
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_1_folder
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file_warn_global_each_final_eachabort_twoeachs_oneoverridden = path_utils.concat_path(self.test_dir, "test_config_file_warn_global_each_final_eachabort_twoeachs_oneoverridden.t20")
        create_and_write_file.create_file_contents(self.test_config_file_warn_global_each_final_eachabort_twoeachs_oneoverridden, cfg_file_contents_warn_global_each_final_eachabort_twoeachs_oneoverridden)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def testArtifactBase1(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [path_utils.basename_filtered(self.folder2)], True, False, 7, True)
        self.assertEqual(artbase.get_path(), self.test_source_folder)
        self.assertEqual(artbase.get_list_exceptions(), [path_utils.basename_filtered(self.folder2)])
        self.assertEqual(artbase.validate_exceptions(), (True, ""))
        self.assertTrue(artbase.get_descend())
        self.assertFalse(artbase.get_abort())
        self.assertEqual(artbase.get_warn_size(), 7)
        self.assertTrue(artbase.get_warn_abort())

    def testArtifactBase2(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [path_utils.basename_filtered(self.nonexistent)], False, True, 2, False)
        self.assertEqual(artbase.get_path(), self.test_source_folder)
        self.assertEqual(artbase.get_list_exceptions(), [path_utils.basename_filtered(self.nonexistent)])
        r = artbase.validate_exceptions()
        self.assertFalse(r[0])
        self.assertFalse(artbase.get_descend())
        self.assertTrue(artbase.get_abort())
        self.assertEqual(artbase.get_warn_size(), 2)
        self.assertFalse(artbase.get_warn_abort())

    def testMakeBackupArtifactsList1(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [ path_utils.basename_filtered(self.folder2) ], True, True, 0, False)
        res = backup_processor.make_backup_artifacts_list([artbase])

        tup = get_tuple_list_index(res, self.folder1)
        self.assertTrue(tup is not None)
        self.assertEqual(res[tup][0], self.folder1)
        self.assertTrue(res[tup][1])
        self.assertEqual(res[tup][2], 0)
        self.assertFalse(res[tup][3])

        tup = get_tuple_list_index(res, self.folder2)
        self.assertTrue(tup is None)

        tup = get_tuple_list_index(res, self.folder3)
        self.assertTrue(tup is not None)
        self.assertEqual(res[tup][0], self.folder3)
        self.assertTrue(res[tup][1])
        self.assertEqual(res[tup][2], 0)
        self.assertFalse(res[tup][3])

    def testMakeBackupArtifactsList2(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [], False, False, 0, True)
        res = backup_processor.make_backup_artifacts_list([artbase])

        tup = get_tuple_list_index(res, self.test_source_folder)
        self.assertTrue(tup is not None)
        self.assertEqual(res[tup][0], self.test_source_folder)

        tup = get_tuple_list_index(res, self.folder1)
        self.assertTrue(tup is None)

        tup = get_tuple_list_index(res, self.folder2)
        self.assertTrue(tup is None)

        tup = get_tuple_list_index(res, self.folder3)
        self.assertTrue(tup is None)

    def testReadConfig(self):
        v, r = backup_processor.read_config(self.test_config_file)
        self.assertTrue(v)
        self.assertEqual(r[0][0], self.prep_filename)
        self.assertEqual(r[0][1], [])
        self.assertEqual(r[2], [self.test_target_1_folder, self.test_target_2_folder])
        self.assertEqual(r[3], self.bk_base_folder_test)
        self.assertEqual(r[4], self.bk_test_temp_folder)
        self.assertEqual( r[5], ( (convert_unit.convert_to_bytes(self.warn_each_1)[1],False) , (convert_unit.convert_to_bytes(self.warn_final_1)[1],False) ) )

    def testReadConfigBlankFilename(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blanksub_blankfn = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blanksub_blankfn))
        create_and_write_file.create_file_contents(blanksub_blankfn, self.cfg_file_contents)
        self.assertTrue(os.path.exists(blanksub_blankfn))

        v, r = backup_processor.read_config(blanksub_blankfn)
        self.assertTrue(v)
        self.assertEqual(r[0][0], self.prep_filename)
        self.assertEqual(r[0][1], [])
        self.assertEqual(r[2], [self.test_target_1_folder, self.test_target_2_folder])
        self.assertEqual(r[3], self.bk_base_folder_test)
        self.assertEqual(r[4], self.bk_test_temp_folder)
        self.assertEqual( r[5], ( (convert_unit.convert_to_bytes(self.warn_each_1)[1],False) , (convert_unit.convert_to_bytes(self.warn_final_1)[1],False) ) )

    def testReadConfigPrepParamEnvVar(self):

        os.environ[ (self.reserved_test_env_var[1:]) ] = self.prep_generated_param_test_filename
        v, r = backup_processor.read_config(self.test_config_file_prep_param)
        self.assertTrue(v)
        self.assertEqual(r[0][0], self.prep_param_filename)
        self.assertEqual(r[0][1], [self.prep_generated_param_test_filename, self.prep_generated_param_test_content])
        self.assertEqual(r[2], [self.test_target_1_folder])
        self.assertEqual(r[3], self.bk_base_folder_test)
        self.assertEqual(r[4], self.bk_test_temp_folder)
        self.assertEqual( r[5], ( (convert_unit.convert_to_bytes(self.warn_each_2)[1],True) , (convert_unit.convert_to_bytes(self.warn_final_2)[1],True) ) )

    def testInvalidConfig1(self):
        v, r = backup_processor.read_config(self.test_malformed_config_file1)
        self.assertFalse(r)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_malformed_config_file1, self.hash_file)
        self.assertFalse(r)

    def testInvalidConfig2(self):
        v, r = backup_processor.read_config(self.test_malformed_config_file2)
        self.assertFalse(r)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_malformed_config_file2, self.hash_file)
        self.assertFalse(r)

    def testInvalidConfig3(self):
        v, r = backup_processor.read_config(self.test_malformed_config_file3)
        self.assertFalse(r)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_malformed_config_file3, self.hash_file)
        self.assertFalse(r)

    def testPrepsWithSpaces1(self):
        v, r = backup_processor.read_config(self.cfg_file_prep_space_1)
        self.assertTrue(r)
        self.assertFalse( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.cfg_file_prep_space_1, self.hash_file)
        self.assertTrue(r)
        self.assertTrue( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )

    def testPrepsWithSpaces2(self):
        v, r = backup_processor.read_config(self.cfg_file_prep_space_2)
        self.assertTrue(r)
        self.assertFalse( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.cfg_file_prep_space_2, self.hash_file)
        self.assertTrue(r)
        self.assertTrue( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )

    def testPrepsWithSpaces3(self):
        v, r = backup_processor.read_config(self.cfg_file_prep_space_3)
        self.assertTrue(r)
        self.assertFalse( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.cfg_file_prep_space_3, self.hash_file)
        self.assertTrue(r)
        self.assertTrue( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )

    def testPrepFails(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.cfg_file_prep_fails, self.hash_file)
        self.assertFalse(r)

    def testPrepParams(self):

        os.environ[ (self.reserved_test_env_var[1:]) ] = self.prep_generated_param_test_filename
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file_prep_param, self.hash_file)
        self.assertTrue(r)
        self.assertTrue( os.path.exists( self.prep_generated_param_test_filename ))
        test_content = ""
        with open(self.prep_generated_param_test_filename) as f:
            test_content = f.read()
        self.assertEqual(test_content, self.prep_generated_param_test_content)

    def testAbortNonexistentBktemp(self):
        v, r = backup_processor.read_config(self.test_config_bktemp_nonexistent_file)
        self.assertTrue(r)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_bktemp_nonexistent_file, self.hash_file)
        self.assertFalse(r)

    def testSkipNonexistentSource(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file_noabort_nonexistent, self.hash_file)
        self.assertTrue(r)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_folder1_e = path_utils.concat_path(tg1_final, "source_test", "folder1.tar.bz2.enc")
        self.assertTrue( os.path.exists( tg1_folder1_e ) )

    def testAbortNonexistentSource(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file_abort_nonexistent, self.hash_file)
        self.assertFalse(r)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_folder1_e = path_utils.concat_path(tg1_final, "source_test", "folder1.tar.bz2.enc")
        self.assertFalse( os.path.exists( tg1_folder1_e ) )

    def testGlobalWarnEachFinalNoAbort(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_noabort)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_noabort, self.hash_file)
        self.assertTrue(v)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_test_source_folder_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test.tar.bz2.enc")
        self.assertTrue( os.path.exists( tg1_test_source_folder_e ) )

    def testGlobalWarnEachAbort(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_abort)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_abort, self.hash_file)
        self.assertFalse(v)

    def testGlobalWarnFinalAbort(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_final_abort)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_final_abort, self.hash_file)
        self.assertFalse(v)

    def testGlobalWarnEachFinalNoAbortEachOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_noabort_each_overridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_noabort_each_overridden, self.hash_file)
        self.assertTrue(v)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_test_source_folder_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test.tar.bz2.enc")
        self.assertTrue( os.path.exists( tg1_test_source_folder_e ) )

    def testGlobalWarnEachFinalNoAbortEachOverriddenAbortOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_noabort_each_overridden_abortoverridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_noabort_each_overridden_abortoverridden, self.hash_file)
        self.assertFalse(v)

    def testGlobalWarnEachFinalEachAbortEachOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_eachabort_each_overridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_eachabort_each_overridden, self.hash_file)
        self.assertFalse(v)

    def testGlobalWarnEachFinalFinalAbortEachOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_finalabort_each_overridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_finalabort_each_overridden, self.hash_file)
        self.assertTrue(v)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_test_source_folder_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test.tar.bz2.enc")
        self.assertTrue( os.path.exists( tg1_test_source_folder_e ) )

    def testGlobalWarnEachFinalFinalAbortTwoEachsOneOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_finalabort_twoeachs_oneoverridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_finalabort_twoeachs_oneoverridden, self.hash_file)
        self.assertTrue(v)
        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg1_test_source_folder_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test.tar.bz2.enc")
        tg1_test_alt_source_folder_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_alt_test.tar.bz2.enc")
        self.assertTrue( os.path.exists( tg1_test_source_folder_e ) )
        self.assertTrue( os.path.exists( tg1_test_alt_source_folder_e ) )

    def testGlobalWarnEachFinalEachAbortTwoEachsOneOverridden(self):
        v, r = backup_processor.read_config(self.test_config_file_warn_global_each_final_eachabort_twoeachs_oneoverridden)
        self.assertTrue(v)
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            v = backup_processor.run_backup(self.test_config_file_warn_global_each_final_eachabort_twoeachs_oneoverridden, self.hash_file)
        self.assertFalse(v)

    def testRunBackup1(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg2_final = path_utils.concat_path(self.test_target_2_folder, self.bk_base_folder_test)

        # check if preparation script was run (it creates a test file)
        self.assertTrue( os.path.exists( path_utils.concat_path( self.prep_generated_test_filename ) ) )

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( path_utils.concat_path(tg1_final, "bk_date.txt")) ) 
        self.assertTrue( os.path.exists( path_utils.concat_path(tg2_final, "bk_date.txt")) ) 

        # check if all artifacts are present on both targets

        # target 1
        tg1_folder1_e = path_utils.concat_path(tg1_final, "source_test", "folder1.tar.bz2.enc")
        tg1_folder1_z = path_utils.concat_path(tg1_final, "source_test", "folder1.tar.bz2")
        tg1_folder1_h = path_utils.concat_path(tg1_final, "source_test", "folder1.tar.bz2.enc.sha256")
        tg1_folder2_e = path_utils.concat_path(tg1_final, "source_test", "folder2.tar.bz2.enc")
        tg1_folder2_z = path_utils.concat_path(tg1_final, "source_test", "folder2.tar.bz2")
        tg1_folder2_h = path_utils.concat_path(tg1_final, "source_test", "folder2.tar.bz2.enc.sha256")
        tg1_folder3_e = path_utils.concat_path(tg1_final, "source_test", "folder3.tar.bz2.enc")
        tg1_folder3_z = path_utils.concat_path(tg1_final, "source_test", "folder3.tar.bz2")
        tg1_folder3_h = path_utils.concat_path(tg1_final, "source_test", "folder3.tar.bz2.enc.sha256")
        tg1_folder4_e = path_utils.concat_path(tg1_final, "source_test", ".folder4.tar.bz2.enc")
        tg1_folder4_z = path_utils.concat_path(tg1_final, "source_test", ".folder4.tar.bz2")
        tg1_folder4_h = path_utils.concat_path(tg1_final, "source_test", ".folder4.tar.bz2.enc.sha256")
        tg1_file0_e = path_utils.concat_path(tg1_final, "source_test", ".file0.txt.tar.bz2.enc")
        tg1_file0_z = path_utils.concat_path(tg1_final, "source_test", ".file0.txt.tar.bz2")
        tg1_file0_h = path_utils.concat_path(tg1_final, "source_test", ".file0.txt.tar.bz2.enc.sha256")

        # target 2
        tg2_folder1_e = path_utils.concat_path(tg2_final, "source_test", "folder1.tar.bz2.enc")
        tg2_folder1_z = path_utils.concat_path(tg2_final, "source_test", "folder1.tar.bz2")
        tg2_folder1_h = path_utils.concat_path(tg2_final, "source_test", "folder1.tar.bz2.enc.sha256")
        tg2_folder2_e = path_utils.concat_path(tg2_final, "source_test", "folder2.tar.bz2.enc")
        tg2_folder2_z = path_utils.concat_path(tg2_final, "source_test", "folder2.tar.bz2")
        tg2_folder2_h = path_utils.concat_path(tg2_final, "source_test", "folder2.tar.bz2.enc.sha256")
        tg2_folder3_e = path_utils.concat_path(tg2_final, "source_test", "folder3.tar.bz2.enc")
        tg2_folder3_z = path_utils.concat_path(tg2_final, "source_test", "folder3.tar.bz2")
        tg2_folder3_h = path_utils.concat_path(tg2_final, "source_test", "folder3.tar.bz2.enc.sha256")
        tg2_folder4_e = path_utils.concat_path(tg2_final, "source_test", ".folder4.tar.bz2.enc")
        tg2_folder4_z = path_utils.concat_path(tg2_final, "source_test", ".folder4.tar.bz2")
        tg2_folder4_h = path_utils.concat_path(tg2_final, "source_test", ".folder4.tar.bz2.enc.sha256")
        tg2_file0_e = path_utils.concat_path(tg2_final, "source_test", ".file0.txt.tar.bz2.enc")
        tg2_file0_z = path_utils.concat_path(tg2_final, "source_test", ".file0.txt.tar.bz2")
        tg2_file0_h = path_utils.concat_path(tg2_final, "source_test", ".file0.txt.tar.bz2.enc.sha256")

        # target1
        self.assertTrue( os.path.exists( tg1_folder1_e ) )
        self.assertTrue( os.path.exists( tg1_folder1_h ) )
        self.assertTrue( os.path.exists( tg1_folder2_e ) )
        self.assertTrue( os.path.exists( tg1_folder2_h ) )
        self.assertTrue( os.path.exists( tg1_folder3_e ) )
        self.assertTrue( os.path.exists( tg1_folder3_h ) )
        self.assertTrue( os.path.exists( tg1_folder4_e ) )
        self.assertTrue( os.path.exists( tg1_folder4_h ) )
        self.assertTrue( os.path.exists( tg1_file0_e ) )
        self.assertTrue( os.path.exists( tg1_file0_h ) )

        # target2
        self.assertTrue( os.path.exists( tg2_folder1_e ) )
        self.assertTrue( os.path.exists( tg2_folder1_h ) )
        self.assertTrue( os.path.exists( tg2_folder2_e ) )
        self.assertTrue( os.path.exists( tg2_folder2_h ) )
        self.assertTrue( os.path.exists( tg2_folder3_e ) )
        self.assertTrue( os.path.exists( tg2_folder3_h ) )
        self.assertTrue( os.path.exists( tg2_folder4_e ) )
        self.assertTrue( os.path.exists( tg2_folder4_h ) )
        self.assertTrue( os.path.exists( tg2_file0_e ) )
        self.assertTrue( os.path.exists( tg2_file0_h ) )

        # check hashes
        # target 1
        self.assertTrue(hash_check.sha256sum_check( tg1_folder1_e, tg1_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder2_e, tg1_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder3_e, tg1_folder3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder4_e, tg1_folder4_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_file0_e, tg1_file0_h ))

        # target 2
        self.assertTrue(hash_check.sha256sum_check( tg2_folder1_e, tg2_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder2_e, tg2_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder3_e, tg2_folder3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder4_e, tg2_folder4_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_file0_e, tg2_file0_h ))

        # decrypt files
        # target 1
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder1_e, tg1_folder1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder2_e, tg1_folder2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder3_e, tg1_folder3_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder4_e, tg1_folder4_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_file0_e, tg1_file0_z, self.passphrase )[0])

        # target 2
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder1_e, tg2_folder1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder2_e, tg2_folder2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder3_e, tg2_folder3_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder4_e, tg2_folder4_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_file0_e, tg2_file0_z, self.passphrase )[0])

        # extract files and check contents
        # target 1
        v, r = tar_wrapper.extract(tg1_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder4_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_file0_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_subfolder1_file2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_subfolder2_file3) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder2_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder3_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder4_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.file0) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

        # target 2
        v, r = tar_wrapper.extract(tg2_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder4_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_file0_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_subfolder1_file2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder2_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder1_subfolder2_file3) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder3_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.folder4_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.file0) ) )

    def testRunBackup2(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg2_final = path_utils.concat_path(self.test_target_2_folder, self.bk_base_folder_test)

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( path_utils.concat_path(tg1_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tg2_final, "bk_date.txt") ) )

        # target 1
        # alt source
        tg1_folder5 = path_utils.concat_path(tg1_final, "source_alt_test", "folder5.tar.bz2.enc")
        tg1_folder6 = path_utils.concat_path(tg1_final, "source_alt_test", "folder6.tar.bz2.enc")
        tg1_file01 = path_utils.concat_path(tg1_final, "source_alt_test", ".file01.txt.tar.bz2.enc")

        # another source
        tg1_folder_another_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another.tar.bz2.enc")
        tg1_folder_another_z = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another.tar.bz2")
        tg1_folder_another_h = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another.tar.bz2.enc.sha256")
        tg1_folder7_e = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc")
        tg1_folder7_z = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2")
        tg1_folder7_h = path_utils.concat_path(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc.sha256")

        # target 2
        # alt source
        tg2_folder5 = path_utils.concat_path(tg2_final, "source_alt_test", "folder5.tar.bz2.enc")
        tg2_folder6 = path_utils.concat_path(tg2_final, "source_alt_test", "folder6.tar.bz2.enc")
        tg2_file01 = path_utils.concat_path(tg2_final, "source_alt_test", ".file01.txt.tar.bz2.enc")

        # another source
        tg2_folder_another_e = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another.tar.bz2.enc")
        tg2_folder_another_z = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another.tar.bz2")
        tg2_folder_another_h = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another.tar.bz2.enc.sha256")
        tg2_folder7_e = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc")
        tg2_folder7_z = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2")
        tg2_folder7_h = path_utils.concat_path(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc.sha256")

        # target 1
        self.assertFalse( os.path.exists( tg1_folder5 ) )
        self.assertTrue( os.path.exists( tg1_folder6 ) )
        self.assertFalse( os.path.exists( tg1_file01 ) )
        self.assertTrue( os.path.exists( tg1_folder_another_e ) )
        self.assertTrue( os.path.exists( tg1_folder_another_h ) )
        self.assertFalse( os.path.exists( tg1_folder7_e ) )
        self.assertFalse( os.path.exists( tg1_folder7_h ) )

        self.assertTrue(hash_check.sha256sum_check( tg1_folder_another_e, tg1_folder_another_h ))

        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder_another_e, tg1_folder_another_z, self.passphrase )[0])

        v, r = tar_wrapper.extract(tg1_folder_another_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.another_folder7) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.file_another) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

        # target 2
        self.assertFalse( os.path.exists( tg2_folder5 ) )
        self.assertTrue( os.path.exists( tg2_folder6 ) )
        self.assertFalse( os.path.exists( tg2_file01 ) )
        self.assertTrue( os.path.exists( tg2_folder_another_e ) )
        self.assertTrue( os.path.exists( tg2_folder_another_h ) )
        self.assertFalse( os.path.exists( tg2_folder7_e ) )
        self.assertFalse( os.path.exists( tg2_folder7_h ) )

        self.assertTrue(hash_check.sha256sum_check( tg2_folder_another_e, tg2_folder_another_h ))

        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder_another_e, tg2_folder_another_z, self.passphrase )[0])

        v, r = tar_wrapper.extract(tg2_folder_another_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.another_folder7) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.file_another) ) )

    def testRunBackup3(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_source_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test)
        tg2_final = path_utils.concat_path(self.test_target_2_folder, self.bk_base_folder_test)

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( path_utils.concat_path(tg1_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tg2_final, "bk_date.txt") ) )

        # target 1
        tg1_space_file1_e = path_utils.concat_path(tg1_final, "special_folder", "   sp_file1.txt.tar.bz2.enc")
        tg1_space_file1_z = path_utils.concat_path(tg1_final, "special_folder", "   sp_file1.txt.tar.bz2")
        tg1_space_file1_h = path_utils.concat_path(tg1_final, "special_folder", "   sp_file1.txt.tar.bz2.enc.sha256")
        tg1_space_file2_e = path_utils.concat_path(tg1_final, "special_folder", "sp_fi  le2.txt.tar.bz2.enc")
        tg1_space_file2_z = path_utils.concat_path(tg1_final, "special_folder", "sp_fi  le2.txt.tar.bz2")
        tg1_space_file2_h = path_utils.concat_path(tg1_final, "special_folder", "sp_fi  le2.txt.tar.bz2.enc.sha256")
        tg1_space_file3_e = path_utils.concat_path(tg1_final, "special_folder", "sp_file3.txt  .tar.bz2.enc")
        tg1_space_file3_z = path_utils.concat_path(tg1_final, "special_folder", "sp_file3.txt  .tar.bz2")
        tg1_space_file3_h = path_utils.concat_path(tg1_final, "special_folder", "sp_file3.txt  .tar.bz2.enc.sha256")
        tg1_quote_file1_e = path_utils.concat_path(tg1_final, "special_folder", "file\"1.txt.tar.bz2.enc")
        tg1_quote_file1_z = path_utils.concat_path(tg1_final, "special_folder", "file\"1.txt.tar.bz2")
        tg1_quote_file1_h = path_utils.concat_path(tg1_final, "special_folder", "file\"1.txt.tar.bz2.enc.sha256")

        tg1_space_folder1_e = path_utils.concat_path(tg1_final, "special_folder", "   sp_folder1.tar.bz2.enc")
        tg1_space_folder1_z = path_utils.concat_path(tg1_final, "special_folder", "   sp_folder1.tar.bz2")
        tg1_space_folder1_h = path_utils.concat_path(tg1_final, "special_folder", "   sp_folder1.tar.bz2.enc.sha256")
        tg1_space_folder2_e = path_utils.concat_path(tg1_final, "special_folder", "sp_fol   der2.tar.bz2.enc")
        tg1_space_folder2_z = path_utils.concat_path(tg1_final, "special_folder", "sp_fol   der2.tar.bz2")
        tg1_space_folder2_h = path_utils.concat_path(tg1_final, "special_folder", "sp_fol   der2.tar.bz2.enc.sha256")
        tg1_space_folder3_e = path_utils.concat_path(tg1_final, "special_folder", "sp_folder3   .tar.bz2.enc")
        tg1_space_folder3_z = path_utils.concat_path(tg1_final, "special_folder", "sp_folder3   .tar.bz2")
        tg1_space_folder3_h = path_utils.concat_path(tg1_final, "special_folder", "sp_folder3   .tar.bz2.enc.sha256")

        # target 2
        tg2_space_file1_e = path_utils.concat_path(tg2_final, "special_folder", "   sp_file1.txt.tar.bz2.enc")
        tg2_space_file1_z = path_utils.concat_path(tg2_final, "special_folder", "   sp_file1.txt.tar.bz2")
        tg2_space_file1_h = path_utils.concat_path(tg2_final, "special_folder", "   sp_file1.txt.tar.bz2.enc.sha256")
        tg2_space_file2_e = path_utils.concat_path(tg2_final, "special_folder", "sp_fi  le2.txt.tar.bz2.enc")
        tg2_space_file2_z = path_utils.concat_path(tg2_final, "special_folder", "sp_fi  le2.txt.tar.bz2")
        tg2_space_file2_h = path_utils.concat_path(tg2_final, "special_folder", "sp_fi  le2.txt.tar.bz2.enc.sha256")
        tg2_space_file3_e = path_utils.concat_path(tg2_final, "special_folder", "sp_file3.txt  .tar.bz2.enc")
        tg2_space_file3_z = path_utils.concat_path(tg2_final, "special_folder", "sp_file3.txt  .tar.bz2")
        tg2_space_file3_h = path_utils.concat_path(tg2_final, "special_folder", "sp_file3.txt  .tar.bz2.enc.sha256")
        tg2_quote_file1_e = path_utils.concat_path(tg2_final, "special_folder", "file\"1.txt.tar.bz2.enc")
        tg2_quote_file1_z = path_utils.concat_path(tg2_final, "special_folder", "file\"1.txt.tar.bz2")
        tg2_quote_file1_h = path_utils.concat_path(tg2_final, "special_folder", "file\"1.txt.tar.bz2.enc.sha256")

        tg2_space_folder1_e = path_utils.concat_path(tg2_final, "special_folder", "   sp_folder1.tar.bz2.enc")
        tg2_space_folder1_z = path_utils.concat_path(tg2_final, "special_folder", "   sp_folder1.tar.bz2")
        tg2_space_folder1_h = path_utils.concat_path(tg2_final, "special_folder", "   sp_folder1.tar.bz2.enc.sha256")
        tg2_space_folder2_e = path_utils.concat_path(tg2_final, "special_folder", "sp_fol   der2.tar.bz2.enc")
        tg2_space_folder2_z = path_utils.concat_path(tg2_final, "special_folder", "sp_fol   der2.tar.bz2")
        tg2_space_folder2_h = path_utils.concat_path(tg2_final, "special_folder", "sp_fol   der2.tar.bz2.enc.sha256")
        tg2_space_folder3_e = path_utils.concat_path(tg2_final, "special_folder", "sp_folder3   .tar.bz2.enc")
        tg2_space_folder3_z = path_utils.concat_path(tg2_final, "special_folder", "sp_folder3   .tar.bz2")
        tg2_space_folder3_h = path_utils.concat_path(tg2_final, "special_folder", "sp_folder3   .tar.bz2.enc.sha256")

        # check existence
        self.assertTrue( os.path.exists( tg1_space_file1_e ) )
        self.assertTrue( os.path.exists( tg1_space_file1_h ) )
        self.assertTrue( os.path.exists( tg1_space_file2_e ) )
        self.assertTrue( os.path.exists( tg1_space_file2_h ) )
        self.assertTrue( os.path.exists( tg1_space_file3_e ) )
        self.assertTrue( os.path.exists( tg1_space_file3_h ) )
        self.assertTrue( os.path.exists( tg1_quote_file1_e ) )
        self.assertTrue( os.path.exists( tg1_quote_file1_h ) )

        self.assertTrue( os.path.exists( tg1_space_folder1_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder1_h ) )
        self.assertTrue( os.path.exists( tg1_space_folder2_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder2_h ) )
        self.assertTrue( os.path.exists( tg1_space_folder3_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder3_h ) )

        # check hashes
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file1_e, tg1_space_file1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file2_e, tg1_space_file2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file3_e, tg1_space_file3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_quote_file1_e, tg1_quote_file1_h ))

        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder1_e, tg1_space_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder2_e, tg1_space_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder3_e, tg1_space_folder3_h ))

        # decrypt generated packages
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file1_e, tg1_space_file1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file2_e, tg1_space_file2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file3_e, tg1_space_file3_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_quote_file1_e, tg1_quote_file1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder1_e, tg1_space_folder1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder2_e, tg1_space_folder2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder3_e, tg1_space_folder3_z, self.passphrase )[0])

        # extract packages
        v, r = tar_wrapper.extract(tg1_space_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_file2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_file3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_quote_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder3_z, self.extracted_folder)
        self.assertTrue(v)

        # check result
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file3) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.quote_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder3) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

        # check existence
        self.assertTrue( os.path.exists( tg2_space_file1_e ) )
        self.assertTrue( os.path.exists( tg2_space_file1_h ) )
        self.assertTrue( os.path.exists( tg2_space_file2_e ) )
        self.assertTrue( os.path.exists( tg2_space_file2_h ) )
        self.assertTrue( os.path.exists( tg2_space_file3_e ) )
        self.assertTrue( os.path.exists( tg2_space_file3_h ) )
        self.assertTrue( os.path.exists( tg2_quote_file1_e ) )
        self.assertTrue( os.path.exists( tg2_quote_file1_h ) )

        self.assertTrue( os.path.exists( tg2_space_folder1_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder1_h ) )
        self.assertTrue( os.path.exists( tg2_space_folder2_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder2_h ) )
        self.assertTrue( os.path.exists( tg2_space_folder3_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder3_h ) )

        # check hashes
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file1_e, tg2_space_file1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file2_e, tg2_space_file2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file3_e, tg2_space_file3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_quote_file1_e, tg2_quote_file1_h ))

        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder1_e, tg2_space_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder2_e, tg2_space_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder3_e, tg2_space_folder3_h ))

        # decrypt generated packages
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file1_e, tg2_space_file1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file2_e, tg2_space_file2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file3_e, tg2_space_file3_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_quote_file1_e, tg2_quote_file1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder1_e, tg2_space_folder1_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder2_e, tg2_space_folder2_z, self.passphrase )[0])
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder3_e, tg2_space_folder3_z, self.passphrase )[0])

        # extract packages
        v, r = tar_wrapper.extract(tg2_space_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_file2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_file3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_quote_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder3_z, self.extracted_folder)
        self.assertTrue(v)

        # check result
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_file3) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.quote_file1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder1) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder2) ) )
        self.assertTrue( os.path.exists( path_utils.concat_path( self.extracted_folder, self.space_folder3) ) )

    def testSpecialTargets1(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_target_config_file, self.hash_file)
        self.assertTrue(r)

        tge1_final = path_utils.concat_path(self.test_target_space_1_folder, self.bk_base_folder_test)
        tge2_final = path_utils.concat_path(self.test_target_space_2_folder, self.bk_base_folder_test)
        tge3_final = path_utils.concat_path(self.test_target_space_3_folder, self.bk_base_folder_test)

        # check if dates were written in all targets
        self.assertTrue( os.path.exists( path_utils.concat_path(tge1_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tge2_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tge3_final, "bk_date.txt") ) )

    def testSpecialBkBaseAndTemp1(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_base_and_temp_config_file1, self.hash_file)
        self.assertTrue(r)
        tg_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test_space_1)
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc") ) )

    def testSpecialBkBaseAndTemp2(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_base_and_temp_config_file2, self.hash_file)
        self.assertTrue(r)
        tg_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test_space_2)
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc") ) )

    def testSpecialBkBaseAndTemp3(self):
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_base_and_temp_config_file3, self.hash_file)
        self.assertTrue(r)
        tg_final = path_utils.concat_path(self.test_target_1_folder, self.bk_base_folder_test_space_3)
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc") ) )

if __name__ == '__main__':
    unittest.main()
