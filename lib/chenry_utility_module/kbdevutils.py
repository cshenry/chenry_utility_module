from __future__ import absolute_import

import sys
import json
import os
from os.path import exists
from pathlib import Path
from configparser import ConfigParser

config_file = os.environ.get("KBDEVUTIL_CONFIG", "/scratch/shared/code/sharedconfig.cfg")
config_parse = ConfigParser()
config_parse.read(config_file)
config = {}
for nameval in config_parse.items("DevEnv"):
    config[nameval[0]] = nameval[1]
sys.path = config["syspaths"].split(";") + sys.path

from installed_clients.WorkspaceClient import Workspace
from kbbasemodules.basemodule import BaseModule
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

class KBDevUtils(BaseModule):
    def __init__(self,study_name,token_file=str(Path.home()) + '/.kbase/token',ws_version="prod",sdkhome="sdkhome",public_output=True):
        wsurl = None
        if ws_version == "prod":
            wsurl = "https://kbase.us/services/ws"
        elif ws_version == "appdev":
            wsurl = "https://appdev.kbase.us/services/ws"
        elif ws_version == "ci":
            wsurl = "https://ci.kbase.us/services/ws"    
        token = None
        with open(token_file, 'r') as fh:
            token = fh.read().strip()
        self.root_path = config["callback_path"]
        self.private_output_path = config["private_output_path"]
        if self.private_output_path[0] != "/":
            self.private_output_path = str(Path.home())+"/"+self.private_output_path
        self.public_output = public_output
        self.public_output_path = config["public_output_path"]
        self.callback_file = self.root_path+"/"+sdkhome+"/kb_sdk_home/run_local/workdir/CallBack.txt"
        self.working_directory = self.root_path+"/"+sdkhome+"/kb_sdk_home/run_local/workdir/tmp/"
        with open(self.callback_file, 'r') as fh:
            callback = fh.read()        
        BaseModule.__init__(self,"KBDevUtils."+study_name,config,config["module_directory"]+"/chenry_utility_module/",str(Path.home()) + "/scratch/" + study_name,token,{"Workspace":Workspace(wsurl, token=token)},callback)
        print("Output files printed to:"+self.notebook_output_dir())
        self.version = "0.1.1.kbdu"
        self.study_name = study_name
        self.msrecon = None
    
    def msseedrecon(self):
        if self.msrecon == None:
            from ModelSEEDReconstruction.modelseedrecon import ModelSEEDRecon
            self.msrecon = ModelSEEDRecon(self.config,self.config["module_directory"]+"/KB-ModelSEEDReconstruction/",self.working_dir,self.token,self.clients,self.callback_url)
        return self.msrecon
    
    def devutil_client(self):
        if "KBDevUtils" not in self.clients:
            from installed_clients.chenry_utility_moduleClient import chenry_utility_module
            self.clients["KBDevUtils"] = chenry_utility_module(self.callback_url,token=self.token)
        return self.clients["KBDevUtils"]
        
    def clear_sdk_dir(self):
        return self.devutil_client().run_command({"command":"clear"})
        
    def sdk_dir_perms(self):
        return self.devutil_client().run_command({"command":"perms"})
    
    def notebook_output_dir(self,public_output=None,create=True):
        if not public_output:
            public_output = self.public_output
        output_path = self.private_output_path+"/"+self.study_name+"/"
        if public_output:
            output_path = self.public_output_path+"/"+self.study_name+"/output/"
        if create:
            if not exists(output_path):
                os.makedirs(output_path, exist_ok=True)
        return output_path
        