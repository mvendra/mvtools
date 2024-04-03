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

    def _read_params(self):

        # params
        source_path = None
        dest_path = None
        accepted_repo_type = None
        bare_clone = None
        remote_name = None
        default_filter = None
        include_list = None
        exclude_list = None

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "source_path is a required parameter"

        # dest_path
        try:
            dest_path = self.params["dest_path"]
        except KeyError:
            return False, "dest_path is a required parameter"

        # accepted_repo_type
        try:
            accepted_repo_type = self.params["accepted_repo_type"]
        except KeyError:
            return False, "accepted_repo_type is a required parameter"

        # bare_clone
        bare_clone_str = ""
        try:
            bare_clone_str = self.params["bare_clone"]
        except KeyError:
            return False, "bare_clone is a required parameter"
        if bare_clone_str == "yes":
            bare_clone = True
        elif bare_clone_str == "no":
            bare_clone = False
        else:
            return False, "bare_clone has an invalid value: [%s]. Accepted values are: yes/no." % bare_clone_str

        # remote_name (only relevant if bare_clone is False)
        if not bare_clone:
            try:
                remote_name = self.params["remote_name"]
            except KeyError:
                return False, "remote_name is a required parameter"

        # default_filter
        try:
            default_filter = self.params["default_filter"]
        except KeyError:
            default_filter = "include"
        if default_filter != "include" and default_filter != "exclude":
            return False, "default_filter has an invalid value: [%s] - valid values are include/exclude" % default_filter

        # include_list
        try:
            include_list_read = self.params["include_list"]
            if not isinstance(include_list_read, list):
                return False, "include_list must be a list"
            include_list = include_list_read
        except KeyError:
            include_list = []

        # exclude_list
        try:
            exclude_list_read = self.params["exclude_list"]
            if not isinstance(exclude_list_read, list):
                return False, "exclude_list must be a list"
            exclude_list = exclude_list_read
        except KeyError:
            exclude_list = []

        return True, (source_path, dest_path, accepted_repo_type, bare_clone, remote_name, default_filter, include_list, exclude_list)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        source_path, dest_path, accepted_repo_type, bare_clone, remote_name, default_filter, include_list, exclude_list = r

        v, r = path_utils.check_if_paths_not_exist_stop_first([source_path, dest_path])
        if not v:
            return False, "path does not exist: [%s]" % r

        v, r = fsquery.makecontentlist(source_path, True, False, False, True, False, True, True, None)
        if not v:
            return False, r
        items = r

        items_filtered_clone = []
        items_filtered_clone_postfs = []
        items_tuple_final = []

        filters_clone = []
        filters_fs = []
        filters_clone.append( (fsquery_adv_filter.filter_is_repo, "not-used") )

        items_filtered_clone = fsquery_adv_filter.filter_path_list_and(items, filters_clone)

        if default_filter == "include":
            filters_fs.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
            for ei in exclude_list:
                filters_fs.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei, "auto")) )
            items_filtered_clone_postfs = fsquery_adv_filter.filter_path_list_and(items_filtered_clone, filters_fs)
        elif default_filter == "exclude":
            filters_fs.append( (fsquery_adv_filter.filter_all_negative, "not-used") )
            for ii in include_list:
                filters_fs.append( (fsquery_adv_filter.filter_has_middle_pieces, path_utils.splitpath(ii, "auto")) )
            items_filtered_clone_postfs = fsquery_adv_filter.filter_path_list_or(items_filtered_clone, filters_fs)

        # pre-assemble final source and target repo paths
        for it in items_filtered_clone_postfs:

            v, r = detect_repo_type.detect_repo_type(it)
            if not v:
                return False, r
            repotype_detected = r

            if repotype_detected == accepted_repo_type:
                middle_path_parts = path_utils.find_middle_path_parts(source_path, it)
                if middle_path_parts is None:
                    return False, "cannot find middle parts of path: [%s vs %s]" % (source_path, it)
                target_repo = path_utils.concat_path( dest_path, middle_path_parts, path_utils.basename_filtered(it) )
                if os.path.exists(target_repo):
                    return False, "target repo [%s] already exists." % target_repo
                items_tuple_final.append( (it, target_repo) )

        # create (clone) repos
        for item_pair in items_tuple_final:
            final_src = item_pair[0]
            final_target = item_pair[1]
            if bare_clone:
                v, r = git_lib.clone_bare(final_src, final_target)
                if not v:
                    return False, "unable to bare-clone [%s] into [%s]." % (final_src, final_target)
            else:
                v, r = git_lib.clone(final_src, final_target, remote_name)
                if not v:
                    return False, "unable to clone [%s] into [%s]." % (final_src, final_target)

        return True, None
