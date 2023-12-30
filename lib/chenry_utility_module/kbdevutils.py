from __future__ import absolute_import

import sys
import json
import os
from os.path import exists
from pathlib import Path
from configparser import ConfigParser
from installed_clients.WorkspaceClient import Workspace
from kbbasemodules.basemodule import BaseModule
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)

class KBDevUtils(BaseModule):
    def __init__(self,study_name,token_file=str(Path.home()) + '/.kbase/token',config_file=str(Path.home()) + '/.kbase/config',ws_version="prod",sdkhome=None,output_root=None):
        # Setting up filenames and checking for existence
        self.token_file = token_file
        if not exists(self.token_file):
            logger.critical("Token file not found! Use the kbdevutils.set_token(<token>) to create the file!")
        self.config_file = config_file
        if not exists(self.config_file):
            logger.critical("You must create a config file in ~/.kbase/config before running this notebook. See instructions: https://docs.google.com/document/d/1fQ6iS_uaaZKbjWtw1MgzqilklttIibNO9XIIJWgxWKo/edit")
            sys.exit(1)
        # Loading config file
        confighash = self.read_config()
        # Setting up workspace URL
        self.ws_version = ws_version
        self.wsurl = self.get_wsurl_from_version(self.ws_version)
        # Setting up token
        token = self.read_token()
        # Setting up paths
        self.codebase = confighash.get("codebase","")
        # Running BaseModule init
        self.study_name = study_name
        # Getting callback url
        self.root_path = confighash.get("callback_path","")
        # Setting up SDK home
        self.sdkhome = sdkhome
        if not self.sdkhome:
            if self.ws_version == "prod":
                self.sdkhome = confighash.get("prod_sdk_home","prod")
            elif self.ws_version == "appdev":
                self.sdkhome = confighash.get("appdev_sdk_home","appdev")
        # Setting up output directory
        if output_root:
            self.output_root = output_root
        else:
            self.output_root = confighash.get("output_root","KBaseAnalysis/")
        if self.output_root[0] != "/":
            self.output_root = str(Path.home())+"/"+self.output_root
        self.set_study_root()
        # Setting the session from file
        self.output_dir = None
        self.read_session()
        print("Output files printed to:"+self.output_dir+" when using KBDevUtils.output_dir")
        # Setting callback directories
        self.callback_file = self.root_path+"/"+self.sdkhome+"/kb_sdk_home/run_local/workdir/CallBack.txt"
        self.working_directory = self.root_path+"/"+self.sdkhome+"/kb_sdk_home/run_local/workdir/tmp/"
        callback = self.read_callback()
        # Initializing BaseModule
        BaseModule.__init__(self,"KBDevUtils."+self.study_name,confighash,self.codebase+"/chenry_utility_module/",str(Path.home()) + "/scratch/" + study_name,token,{"Workspace":Workspace(self.wsurl, token=token)},callback)
        self.version = "0.1.1.kbdu"
        self.msrecon = None
    
    def get_wsurl_from_version(self,version):
        if version == "prod":
            return "https://kbase.us/services/ws"
        elif version == "appdev":
            return "https://appdev.kbase.us/services/ws"
        elif version == "ci":
            return "https://ci.kbase.us/services/ws"
        else:
            logger.critical("Unknown workspace version: "+version)
            return "https://kbase.us/services/ws"

    def read_config(self):
        confighash = {}
        config = ConfigParser()
        config.read(self.config_file)
        for nameval in config.items("DevEnv"):
            confighash[nameval[0]] = nameval[1]
        return confighash

    def read_token(self):
        token = None
        with open(self.token_file, 'r') as fh:
            token = fh.read().strip()
        return token

    def read_callback(self):
        callback = None
        if exists(self.callback_file):
            with open(self.callback_file, 'r') as fh:
                callback = fh.read()
        return callback

    def check_kbase_dir(self):
        if not exists(str(Path.home()) + '/.kbase'):
            os.makedirs(str(Path.home()) + '/.kbase')
    
    def msseedrecon(self):
        if self.msrecon == None:
            from ModelSEEDReconstruction.modelseedrecon import ModelSEEDRecon
            self.msrecon = ModelSEEDRecon(self.config,self.codebase+"/KB-ModelSEEDReconstruction/",self.working_dir,self.token,self.clients,self.callback_url)
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
    
    def set_study_root(self,create=True):
        self.study_root = self.output_root+"/"+self.study_name+"/"
        if not exists(self.study_root):
            os.makedirs(self.study_root, exist_ok=True)
    
    def set_token(self,token):
        self.check_kbase_dir()
        with open(self.token_file, 'w') as fh:
            fh.write(token)

    # Code related to sessions
    def list_sessions(self):
        if exists(self.study_root+"/sessions"):
            return os.listdir(self.study_root+"/sessions")
        else:
            return []
    
    def read_session(self):
        session = "default"
        if exists(self.study_root+"/session"):
            with open(self.study_root+"/session", 'r') as fh:
                session = fh.read()
        else:
            self.set_session(session)
        self.output_dir = self.study_root+"/sessions/"+session+"/output"
        self.data_dir = self.study_root+"/sessions/"+session+"/data"
        return session
    
    def create_session(self,name):
        if not exists(self.study_root+"/sessions/"+name+"/data"):
            os.makedirs(self.study_root+"/sessions/"+name+"/data", exist_ok=True)
            os.makedirs(self.study_root+"/sessions/"+name+"/output", exist_ok=True)

    def set_session(self,name):
        if not exists(self.study_root+"/sessions/"+name):
            self.create_session(name)
        with open(self.study_root+"/session", 'w') as fh:
            fh.write(name)
        self.session = name
        self.output_dir = self.study_root+"/sessions/"+name+"/output"
        self.data_dir = self.study_root+"/sessions/"+name+"/data"

    def copy_session(self,source,target):
        source_dir = source
        if source_dir[0] != "/":
            source_dir = self.study_root+"/sessions/"+source
        if not exists(self.study_root+"/sessions/"+source):
            logger.critical("Source session does not exist!")
        elif exists(self.study_root+"/sessions/"+target):
            logger.critical("Target session already exists!")
        else:
            os.system("cp -r "+source_dir+" "+self.study_root+"/sessions/"+target)

    def clear_session(self,name=None):
        if not name:
            name = self.session
        if exists(self.study_root+"/sessions/"+name):
            os.system("rm -r "+self.study_root+"/sessions/"+name)
        else:
            logger.critical("Session "+name+" does not exist!")

    # Code for saving and loading data
    def save(self,name,data):
        filename = self.data_dir + "/" + name + ".json"
        with open(filename, 'w') as f:
            json.dump(data,f,indent=4,skipkeys=True)

    def load(self,name):
        filename = self.data_dir + "/" + name + ".json"
        with open(filename, 'r') as f:
            return json.load(f)
        
    def list(self):
        files = os.listdir(self.data_dir)
        return [x.split(".")[0] for x in files if x.endswith(".json")]

        