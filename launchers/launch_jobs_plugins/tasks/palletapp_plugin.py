#!/usr/bin/env python

import os

import launch_jobs
import path_utils
import palletapp_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "pallet"

    def _read_params(self):

        operation = None
        archive = None
        path = None
        route = None

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "operation is a required parameter"

        # archive
        try:
            archive = self.params["archive"]
        except KeyError:
            return False, "archive is a required parameter"

        # path
        try:
            path_read = self.params["path"]
            if isinstance(path_read, list):
                path = path_read
            else:
                path = []
                path.append(path_read)
        except KeyError:
            pass # optional

        # route
        try:
            route_read = self.params["route"]
            if isinstance(route_read, list):
                route = route_read
            else:
                route = []
                route.append(route_read)
        except KeyError:
            pass # optional

        return True, (operation, archive, path, route)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        operation, archive, path, route = r

        # delegate
        if operation == "init":
            return self.task_init(feedback_object, archive)
        elif operation == "create":
            return self.task_create(feedback_object, archive, path)
        elif operation == "extract":
            return self.task_extract(feedback_object, archive, path)
        elif operation == "load":
            return self.task_load(feedback_object, archive, path)
        elif operation == "ditch":
            return self.task_ditch(feedback_object, archive, route)
        elif operation == "export":
            return self.task_export(feedback_object, archive, route, path)
        elif operation == "list":
            return self.task_list(feedback_object, archive)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_init(self, feedback_object, archive):

        v, r = palletapp_wrapper.init(archive)
        if not v:
            return False, r
        return True, None

    def task_create(self, feedback_object, archive, path):

        if path is None:
            return False, "path is a required parameter, for the create operation"

        v, r = palletapp_wrapper.create(archive, path[0])
        if not v:
            return False, r
        return True, None

    def task_extract(self, feedback_object, archive, path):

        if path is None:
            return False, "path is a required parameter, for the extract operation"

        v, r = palletapp_wrapper.extract(archive, path[0])
        if not v:
            return False, r
        return True, None

    def task_load(self, feedback_object, archive, path):

        if path is None:
            return False, "path is a required parameter, for the load operation"

        for cur_path in path:
            v, r = palletapp_wrapper.load(archive, cur_path)
            if not v:
                return False, r

        return True, None

    def task_ditch(self, feedback_object, archive, route):

        if route is None:
            return False, "route is a required parameter, for the ditch operation"

        for cur_route in route:
            v, r = palletapp_wrapper.ditch(archive, cur_route)
            if not v:
                return False, r

        return True, None

    def task_export(self, feedback_object, archive, route, path):

        if route is None:
            return False, "route is a required parameter, for the export operation"

        if path is None:
            return False, "path is a required parameter, for the export operation"

        v, r = palletapp_wrapper.export(archive, route[0], path[0])
        if not v:
            return False, r
        return True, None

    def task_list(self, feedback_object, archive):

        v, r = palletapp_wrapper.list(archive)
        if not v:
            return False, r

        feedback_object("Archive contents:")
        for line in r.split(os.linesep):
            feedback_object(line)
        return True, None
