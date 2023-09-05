# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import time
import sys
from os.path import exists
from installed_clients.KBaseReportClient import KBaseReport
#END_HEADER


class chenry_utility_module:
    '''
    Module Name:
    chenry_utility_module

    Module Description:
    A KBase module: chenry_utility_module
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/cshenry/chenry_utility_module.git"
    GIT_COMMIT_HASH = "7e3c1c0b7787459f745d935444e44eb08ab38380"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.workspaceURL = config['workspace-url']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def activate_callback_server(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of mapping from String to unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN activate_callback_server
        f = open("/kb/module/work/CallBack.txt","w")
        f.write(self.callback_url)
        f.close()
        end = False
        while end == False:
            time.sleep(10)
            if exists("/kb/module/work/__DONE__"):
                end = True
        output = {}
        os.remove("/kb/module/work/__DONE__")
        #END activate_callback_server

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method activate_callback_server return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_command(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of mapping from String to unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_command
        output = {}
        if params["command"] == "clear":
            os.system("rm -rf /kb/module/work/tmp/*")
            output["comments"] = "Temp directory cleared"
        if params["command"] == "perms":
            os.system("chmod a+w -R /kb/module/work/tmp")
            output["comments"] = "Write perms granted to temp directory"
        #END run_command

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_command return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
