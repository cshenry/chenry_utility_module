from __future__ import absolute_import

import sys
import json
import os
from os.path import exists
from pathlib import Path
from configparser import ConfigParser

codebase = os.environ.get("CODE_BASE","/scratch/shared/code")
config_file = os.environ.get("KBDEVUTIL_CONFIG", codebase+"/sharedconfig.cfg")
config_parse = ConfigParser()
config_parse.read(config_file)
config = {}
for nameval in config_parse.items("DevEnv"):
    config[nameval[0]] = nameval[1]
paths = config["syspaths"].split(";")
for i,filepath in enumerate(paths):
    if filepath[0:1] != "/":
        paths[i] = codebase+"/"+filepath
sys.path = paths + sys.path

from installed_clients.WorkspaceClient import Workspace
from kbbasemodules.basemodule import BaseModule
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

class KBDevUtils(BaseModule):
    def __init__(self,study_name,token_file=str(Path.home()) + '/.kbase/token',ws_version="prod",sdkhome=None,output_root=None):
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
        self.root_path = config.get("callback_path","")    
        if output_root:
            self.output_root = output_root
        else:
            self.output_root = config.get("output_root","KBaseAnalysis/")
        if self.output_root[0] != "/":
            self.output_root = str(Path.home())+"/"+self.output_root
        if not sdkhome:
            if ws_version == "prod":
                sdkhome = config.get("prod_sdk_home","prod")
            elif ws_version == "appdev":
                sdkhome = config.get("appdev_sdk_home","appdev")
        self.callback_file = self.root_path+"/"+sdkhome+"/kb_sdk_home/run_local/workdir/CallBack.txt"
        self.working_directory = self.root_path+"/"+sdkhome+"/kb_sdk_home/run_local/workdir/tmp/"
        callback = None
        if exists(self.callback_file):
            with open(self.callback_file, 'r') as fh:
                callback = fh.read()     
        BaseModule.__init__(self,"KBDevUtils."+study_name,config,codebase+"/chenry_utility_module/",str(Path.home()) + "/scratch/" + study_name,token,{"Workspace":Workspace(wsurl, token=token)},callback)
        self.version = "0.1.1.kbdu"
        self.study_name = study_name
        print("Output files printed to:"+self.out_dir()+" when using KBDevUtils.out_dir()")
        self.msrecon = None
    
    def msseedrecon(self):
        if self.msrecon == None:
            from ModelSEEDReconstruction.modelseedrecon import ModelSEEDRecon
            self.msrecon = ModelSEEDRecon(self.config,codebase+"/KB-ModelSEEDReconstruction/",self.working_dir,self.token,self.clients,self.callback_url)
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
    
    def out_dir(self,create=True):
        output_path = self.output_root+"/"+self.study_name+"/"
        if create:
            if not exists(output_path):
                os.makedirs(output_path, exist_ok=True)
        return output_path
        