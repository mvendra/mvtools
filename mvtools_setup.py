#!/usr/bin/env python3

import sys
import os
import subprocess

# reminder: importing anything here other than vanilla python modules is forbidden

def _local_add2pythonpath(env_param, path):

    local_env = env_param
    pyenvvar = "PYTHONPATH"

    if not pyenvvar in local_env:
        local_env[pyenvvar] = path
    else:
        local_env[pyenvvar] = "%s:%s" % (local_env[pyenvvar], path)

    return local_env

def _resolve_path(path):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def pre_generate_genlinks_links(mvtools_path, links_path):

    # genlinks itself requires some links
    # this function's objective is to pre-create them so genlinks itself can run and do its job

    os.mkdir(links_path)

    source_items_templ  = ["path_utils.py", "fsquery.py", "fsquery_adv_filter.py", "detect_repo_type.py", "mvtools_envvars.py"]
    source_items_templ += ["git/git_lib.py", "wrappers/git_wrapper.py"]
    source_items_templ += ["svn/svn_lib.py", "wrappers/svn_wrapper.py"]
    source_items_templ += ["parsing_dsl/dsl_type20.py", "parsing_dsl/miniparse.py"]
    source_items_templ += ["launchers/generic_run.py"]

    source_items = []
    for sit in source_items_templ:
        source_items.append("%s%s%s" % (mvtools_path, "/", sit))

    for si in source_items:
        di = os.path.join(links_path, os.path.basename(si))
        os.symlink(si, di)

def run_genlinks(mvtools_path, links_path):

    use_env = os.environ.copy()
    use_env["MVTOOLS"] = mvtools_path
    use_env["MVTOOLS_LINKS_PATH"] = links_path
    use_env = _local_add2pythonpath(use_env, links_path)

    genlinks_path = "%s%s%s" % (mvtools_path, "/", "genlinks.py")

    try:
        process = subprocess.run([genlinks_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=use_env)
        if process.returncode==0:
            return True, None
        else:
            return False, "genlinks process call failed."
    except Exception as ex:
        return False, "genlinks process call failed: [%s]." % (str(ex))

def generate_mvtools_profile(mvtools_path, temp_path, links_path, toolbus_dbs_path, git_visitor_path, cygwin_install_path):

    contents = ""

    contents += "export MVTOOLS=\"%s\"\n" % mvtools_path
    contents += "export MVTOOLS_LINKS_PATH=\"%s\"\n" % links_path
    contents += "export MVTOOLS_TEMP_PATH=\"%s\"\n" % temp_path
    contents += "export MVTOOLS_TOOLBUS_BASE=\"%s\"\n" % toolbus_dbs_path
    contents += "export MVTOOLS_GIT_VISITOR_BASE=\"%s\"\n" % git_visitor_path
    if cygwin_install_path is not None:
        contents += "export MVTOOLS_CYGWIN_INSTALL_PATH=\"%s\"\n" % cygwin_install_path
    contents += "source $MVTOOLS/mvtools_main.sh"

    return contents

def run_uts(mvtools_path, links_path):

    use_env = os.environ.copy()
    use_env["MVTOOLS"] = mvtools_path
    use_env["MVTOOLS_LINKS_PATH"] = links_path
    use_env = _local_add2pythonpath(use_env, links_path)

    uts_script_path = "%s%s%s%s%s" % (mvtools_path, "/", "tests", "/", "run_all_mvtools_tests.py")

    try:
        process = subprocess.run([uts_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=use_env)
        if process.returncode==0:
            return True, None
        else:
            return False, "run_all_mvtools_tests process call failed."
    except Exception as ex:
        return False, "run_all_mvtools_tests process call failed: [%s]." % (str(ex))

def mvtools_setup(profile_filename, mvtools_path, temp_path, links_path, toolbus_dbs_path, git_visitor_path, cygwin_install_path, run_unit_tests):

    if profile_filename is not None:
        profile_filename = _resolve_path(profile_filename)
        if os.path.exists(profile_filename):
            print("Profile filename [%s] already exists. Will abort to avoid overwritting." % profile_filename)
            return False

    print("This script will help you install mvtools.")
    print("")

    # main envvar
    if mvtools_path is None:
        print("Mvtools requires the 'MVTOOLS' envvar to point to the installation folder.")
        mvtools_path = input("Choose your mvtools instalation folder (must preexist - leave empty for automatic discovery):")
        print("")
    if mvtools_path == "":
        mvtools_path = os.getcwd()
    mvtools_path_copy = mvtools_path
    mvtools_path = _resolve_path(mvtools_path)
    if not os.path.exists(mvtools_path):
        print("The chosen path for the mvtools main path [%s] is invalid. Aborting..." % mvtools_path)
        return False
    mvtools_path_sanity_test = os.path.join(mvtools_path, os.path.basename(__file__))
    if not os.path.exists(mvtools_path_sanity_test):
        print("The chosen path for the mvtools main path [%s] seems to be invalid. Aborting..." % mvtools_path)
        return False

    if temp_path is None:
        print("Mvtools requires a local folder for temporary storage.")
        temp_path = input("Choose your local temp folder (must preexist):")
        print("")
    temp_path_copy = temp_path
    temp_path = _resolve_path(temp_path)
    if not os.path.exists(temp_path):
        print("The chosen path for mvtool's temp path [%s] does not exist. Aborting..." % temp_path)
        return False

    # links folder
    if links_path is None:
        print("Mvtools requires a local folder to store its links.")
        links_path = input("Choose your local links folder (must not preexist):")
        print("")
    links_path_copy = links_path
    links_path = _resolve_path(links_path)
    if os.path.exists(links_path):
        print("The chosen path for mvtool's links path [%s] already exists. Aborting..." % links_path)
        return False

    # toolbus databases
    if toolbus_dbs_path is None:
        print("Mvtools requires a local folder to store its toolbus databases.")
        toolbus_dbs_path = input("Choose your local toolbus databases folder (must preexist):")
        print("")
    toolbus_dbs_path_copy = toolbus_dbs_path
    toolbus_dbs_path = _resolve_path(toolbus_dbs_path)
    if not os.path.exists(toolbus_dbs_path):
        print("The chosen path for toolbus's databases path [%s] is invalid. Aborting..." % toolbus_dbs_path)
        return False

    # git-visitor search path
    if git_visitor_path is None:
        print("Mvtools requires the definition of a base path to search for git repos, for git-visitor to use.")
        git_visitor_path = input("Choose your local search path for your git repos you want git-visitor to use (must preexist):")
        print("")
    git_visitor_path_copy = git_visitor_path
    git_visitor_path = _resolve_path(git_visitor_path)
    if not os.path.exists(git_visitor_path):
        print("The chosen path for git-visitor's path [%s] is invalid. Aborting..." % git_visitor_path)
        return False

    # cygwin install path
    cygwin_install_path_read = ""
    if cygwin_install_path is None:
        print("Mvtools can be hooked with the local system's cygwin installation path, for correct cygwin-to-windows paths resolution. This is optional.")
        cygwin_install_path_read = input("Choose your local path that points to this system's cygwin installation path (optional - can be left blank - must be a windows path, not a cygwin path - can't contain environment variables or any other aliases of any kind):")
        print("")
    if cygwin_install_path_read == "":
        cygwin_install_path_copy = None
    else:
        cygwin_install_path_copy = cygwin_install_path_read
        cygwin_install_path = cygwin_install_path_read
        if not os.path.exists(cygwin_install_path):
            print("The chosen path for this system's cygwin installation path [%s] is invalid. Aborting..." % cygwin_install_path)
            return False

    # links
    print("Generating links...")
    pre_generate_genlinks_links(mvtools_path, links_path)
    v, r = run_genlinks(mvtools_path, links_path)
    if not v:
        print(r)
        return False
    print("")

    # receipt / confirmation
    print("Will generate an installation profile with the following variables:")
    print("[%s] for MVTOOLS" % mvtools_path_copy)
    print("[%s] for MVTOOLS_TEMP_PATH" % temp_path_copy)
    print("[%s] for MVTOOLS_LINKS_PATH" % links_path_copy)
    print("[%s] for MVTOOLS_TOOLBUS_BASE" % toolbus_dbs_path_copy)
    print("[%s] for MVTOOLS_GIT_VISITOR_BASE" % git_visitor_path_copy)
    print("[%s] for MVTOOLS_CYGWIN_INSTALL_PATH" % cygwin_install_path_copy)
    print("")

    # generate profile
    generated_contents = generate_mvtools_profile(mvtools_path_copy, temp_path_copy, links_path_copy, toolbus_dbs_path_copy, git_visitor_path_copy, cygwin_install_path_copy)
    if profile_filename is None:
        print("# --- BEGIN GENERATED PROFILE CONTENTS ---")
        print(generated_contents)
        print("# --- END GENERATED PROFILE CONTENTS ---")
    else:
        with open(profile_filename, "w") as f:
            f.write(generated_contents)
        print("Wrote mvtool's installation profile file: [%s]." % profile_filename)
    print("")

    if run_unit_tests:
        print("Will run unit tests...")
        v, r = run_uts(mvtools_path, links_path)
        if not v:
            print(r)
            print("Please note that the UTs will fail if some external dependencies are missing. Try sourcing the generated profile and then running the unit tests manually at tests/run_all_mvtools_tests.py for details.")
            return False
        print("Finished running unit tests: All successful.")
        print("")

    last_message = ""
    if profile_filename is None:
        last_message = "Now either create a file with the generated, printed contents above and then source it in your .bashrc, or add the contents directly onto your .bashrc."
    else:
        last_message = "Now either source the generated profile file or add its generated contents directly into your .bashrc."

    print("Mvtools setup is complete. %s" % last_message)
    return True

def puaq():
    print("Valid options are:")
    print("[--profile-filename] -> defines the bash file to write the installation recipe to. If ommitted, its contents will be printed to stdout.")
    print("[--mvtools-path] -> defines the MVTOOLS envvar. It should point to the mvtools base folder. If ommitted, it will be prompted from stdin.")
    print("[--temp-path] -> defines the MVTOOLS_TEMP_PATH envvar. If ommitted, it will be prompted from stdin.")
    print("[--links-path] -> defines the MVTOOLS_LINKS_PATH envvar. If ommitted, it will be prompted from stdin.")
    print("[--toolbus-db-path] -> defines the MVTOOLS_TOOLBUS_BASE envvar. If ommitted, it will be prompted from stdin.")
    print("[--git-visitor-path] -> defines the MVTOOLS_GIT_VISITOR_BASE envvar. If ommitted, it will be prompted from stdin.")
    print("[--cygwin-install-path] -> defines the MVTOOLS_CYGWIN_INSTALL_PATH envvar (must be a windows path, not a cygwin path, can't contain environment variables or any other aliases of any kind). If ommitted, it will be prompted from stdin.")
    print("[--run-uts] -> runs mvtools's unit tests after setup.")
    sys.exit(0)

if __name__ == "__main__":

    options = sys.argv[1:]

    if "--help" in options:
        puaq()

    # switches
    run_unit_tests = False

    # options
    profile_filename = None
    profile_filename_next = False

    mvtools_path = None
    mvtools_path_next = False

    temp_path = None
    temp_path_next = False

    links_path = None
    links_path_next = False

    toolbus_dbs_path = None
    toolbus_dbs_path_next = False

    git_visitor_path = None
    git_visitor_path_next = False

    cygwin_install_path = None
    cygwin_install_path_next = False

    for o in options:

        if profile_filename_next:
            profile_filename_next = False
            profile_filename = o
            continue

        if mvtools_path_next:
            mvtools_path_next = False
            mvtools_path = o
            continue

        if temp_path_next:
            temp_path_next = False
            temp_path = o
            continue

        if links_path_next:
            links_path_next = False
            links_path = o
            continue

        if toolbus_dbs_path_next:
            toolbus_dbs_path_next = False
            toolbus_dbs_path = o
            continue

        if git_visitor_path_next:
            git_visitor_path_next = False
            git_visitor_path = o
            continue

        if cygwin_install_path_next:
            cygwin_install_path_next = False
            cygwin_install_path = o
            continue

        if o == "--profile-filename":
            profile_filename_next = True
            continue

        if o == "--mvtools-path":
            mvtools_path_next = True
            continue

        if o == "--temp-path":
            temp_path_next = True
            continue

        if o == "--links-path":
            links_path_next = True
            continue

        if o == "--toolbus-db-path":
            toolbus_dbs_path_next = True
            continue

        if o == "--git-visitor-path":
            git_visitor_path_next = True
            continue

        if o == "--cygwin-install-path":
            cygwin_install_path_next = True
            continue

        if o == "--run-uts":
            run_unit_tests = True
            continue

    if not mvtools_setup(profile_filename, mvtools_path, temp_path, links_path, toolbus_dbs_path, git_visitor_path, cygwin_install_path, run_unit_tests):
        sys.exit(1)
