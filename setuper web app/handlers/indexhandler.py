#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tornado.web import authenticated
from basehandlers import BaseHandler
import logging
import json
import shutil
import subprocess


class IndexHandler(BaseHandler):

    count = 0

    @authenticated
    def get(self):
        self.render("index.html", title="Cloud Setuper", username=self.current_user)

    @authenticated
    def post(self):
        softwarename = self.get_argument("softwarename", "")
        softwareauthor = self.get_argument("softwareauthor", "")
        softwareemail = self.get_argument("softwareemail", "")
        softwarecompany = self.get_argument("softwarecompany", "")
        main_progressbar_on = self.get_argument("main_progressbar_on", "")
        desktoplink_on = self.get_argument("desktoplink_on", "")
        language = self.get_argument("language", "zh_CN")
        files =  self.get_arguments("files", [])
        software = {
            'softwarename': softwarename,
            'softwareauthor': softwareauthor,
            'softwareemail': softwareemail,
            'softwarecompany': softwarecompany,
            'main_progressbar_on': main_progressbar_on,
            'desktoplink_on': desktoplink_on,
            'language': language,
            'files': files,
            'OutputFolderName': softwarename
        }
        result = self.checkSoftware(software)
        if result['status']:
            link = self.onesetup(software)
            response = {
                'status': "success",
                'info': result['info'],
                'link': link
            }
            self.count += 1
        else:
            response = {
                'status': "fail",
                'info': result['info'],
                'link': ""
            }
        self.write(response)

    def checkSoftware(self, software):
        if software['softwarename']:
            return {
                'status': True,
                'info': "new software"
            }
        else:
            return {
                'status': False,
                'info': "Software name must be assigned."
            }

    def onesetup(self, software):
        files = []
        staticfilesfloder = os.sep.join([os.getcwd(), 'static', 'files'])
        userfolder = os.sep.join([os.getcwd(), 'static', 'files', self.current_user])
        if not os.path.exists(userfolder):
            os.mkdir(userfolder)
        softwarefolder = os.sep.join([os.getcwd(), 'static', 'files', self.current_user, software['softwarename']])
        if not os.path.exists(softwarefolder):
            os.mkdir(softwarefolder)
        for item in software['files']:
            if os.path.exists(os.sep.join([staticfilesfloder, item])):
                shutil.move(os.sep.join([staticfilesfloder, item]), os.sep.join([softwarefolder, item]))
            f = {}
            f['name'] = item
            f['path'] = item
            files.append(f)
        software['files'] = files

        fd = open(os.sep.join([softwarefolder, 'package.json']), 'wb')
        fd.write(json.dumps(software, indent=4))
        fd.close()

        toolPath = os.sep.join([staticfilesfloder, 'tools'])

        cwd = os.getcwd()
        os.chdir(toolPath)
        subprocess.Popen(['python', 'installcopy.py','-p', '%s'%softwarefolder, '-u', '%s.exe' % software['softwarename']], shell=False)
        os.chdir(cwd)

        return '/'.join([self.settings['static_path'], 'files', self.current_user, software['softwarename'], '%s.exe' % software['softwarename']])
