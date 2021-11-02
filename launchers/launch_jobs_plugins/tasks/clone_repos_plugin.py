#!/usr/bin/env python3

import os

import launch_jobs
import fsquery
import fsquery_adv_filter
import path_utils
import detect_repo_type
import git_lib

class CustomTask(launch_jobs.BaseTask):
    def get_desc(self):
        return "clone_repos"
    def run_task(self, feedback_object, execution_name=None):

        # read out required parameters
        # source_path
        try:
            src_path = self.params["source_path"]
        except KeyError:
            return False, "clone_repos failed - source_path is a required parameter"

        # dest_path
        try:
            dst_path = self.params["dest_path"]
        except KeyError:
            return False, "clone_repos failed - dest_path is a required parameter"

        # accepted_repo_type
        try:
            accepted_repo_type = self.params["accepted_repo_type"]
        except KeyError:
            return False, "clone_repos failed - accepted_repo_type is a required parameter"

        # bare_clone
        try:
            bare_clone_str = self.params["bare_clone"]
        except KeyError:
            return False, "clone_repos failed - bare_clone is a required parameter"
        bare_clone = None
        if bare_clone_str == "yes":
            bare_clone = True
        elif bare_clone_str == "no":
            bare_clone = False
        else:
            return False, "clone_repos failed - bare_clone has an invalid value: [%s]. Accepted values are: yes/no." % bare_clone_str

        # remote_name (only relevant if bare_clone is False)
        if not bare_clone:
            try:
                remote_name = self.params["remote_name"]
            except KeyError:
                return False, "clone_repos failed - remote_name is a required parameter"

        v, r = path_utils.check_if_paths_not_exist_stop_first([src_path, dst_path])
        if not v:
            return False, "clone_repos failed - path does not exist: [%s]" % r

        items = []
        items = fsquery.makecontentlist(src_path, True, False, False, True, False, True, True, None)

        items_filtered_struct = []
        items_filtered_struct_pre = []
        filters_struct = []
        filters_struct.append( (fsquery_adv_filter.filter_has_not_middle_repos, "not-used") )
        filters_struct.append( (fsquery_adv_filter.filter_is_not_repo, "not-used") )

        items_filtered_clone = []
        filters_clone = []
        filters_clone.append( (fsquery_adv_filter.filter_is_repo, "not-used") )

        items_filtered_struct_pre = fsquery_adv_filter.filter_path_list_and(items, filters_struct)
        items_filtered_clone = fsquery_adv_filter.filter_path_list_and(items, filters_clone)

        for it in items_filtered_struct_pre:
            middle_path_parts = path_utils.find_middle_path_parts(src_path, it)
            target_struct = path_utils.concat_path(dst_path, middle_path_parts, path_utils.basename_filtered(it))
            items_filtered_struct.append(target_struct)

        # check if any of the plain struct target folders already exist
        v, r = path_utils.check_if_paths_exist_stop_first(items_filtered_struct)
        if not v:
            return False, "clone_repos failed - path already exists: [%s] (failed while creating plain folders structure)" % r

        # create structure (plain folders only)
        for it in items_filtered_struct:
            os.mkdir(it)

        items_tuple_final = []

        # pre-assemble final source and target repo paths
        for it in items:

            v, r = detect_repo_type.detect_repo_type(it)
            if not v:
                return False, r
            repotype_detected = r

            if repotype_detected == accepted_repo_type:
                middle_path_parts = path_utils.find_middle_path_parts(src_path, it)
                if middle_path_parts is None:
                    return False, "clone_repos failed - cannot find middle parts of path: [%s vs %s]" % (src_path, it)
                target_repo = path_utils.concat_path( dst_path, middle_path_parts, path_utils.basename_filtered(it) )
                if os.path.exists(target_repo):
                    return False, "clone_repos failed - target repo [%s] already exists." % target_repo
                items_tuple_final.append( (it, target_repo) )

        # create (clone) repos
        for item_pair in items_tuple_final:
            final_src = item_pair[0]
            final_target = item_pair[1]
            if bare_clone:
                v, r = git_lib.clone_bare(final_src, final_target)
                if not v:
                    return False, "clone_repos failed - unable to bare-clone [%s] into [%s]." % (final_src, final_target)
            else:
                v, r = git_lib.clone(final_src, final_target, remote_name)
                if not v:
                    return False, "clone_repos failed - unable to clone [%s] into [%s]." % (final_src, final_target)

        return True, None
