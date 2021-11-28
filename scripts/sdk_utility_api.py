import argparse
import sys
import logging
import os
import time
from os.path import exists

logger = logging.getLogger(__name__)

def debug_module(module_dir,sdk_home = None,shared_port = None):
    if shared_port == None:
        shared_port = "8888"
    if isinstance(shared_port, int):
        shared_port = str(shared_port)
    if sdk_home == None:
        sdk_home = os.environ['KB_SDK_HOME']
    callback = None
    if exists(sdk_home+"/run_local/workdir/CallBack.txt"):
        callbackfile = open(sdk_home+"/run_local/workdir/CallBack.txt", "r")
        callback = callbackfile.read()
        callbackfile.close()
    else:
        print("Activate a call back server in a separate terminal before running this command!")
        sys.exit()
    array = module_dir.split("/")
    module_name = array[-1]
    if len(module_name) == 0:
        module_name = array[-2]
    script_dir = module_dir+"/test_local"
    port = ""
    if shared_port != None:
        port = " -p "+shared_port+":"+shared_port        
    print("Once logged in. run this command to install jupyter if not already installed: pip install notebook")
    print("If you are running this alot, we recomend adding \"RUN pip install notebook\" to your dockerfile")
    print("Once inside the container, run this command to activate jupyter server: jupyter notebook --ip 0.0.0.0 --no-browser --allow-root")
    print("Then you can reach your notebook from this address on your browser: http://localhost:"+port+"/")
    os.system(script_dir+"/run_docker.sh run"+port+" -i -t -v "+script_dir+"/workdir:/kb/module/work -v "+sdk_home+"/run_local/workdir/tmp:/kb/module/work/tmp -v "+script_dir+"/refdata:/data:ro -e \"SDK_CALLBACK_URL="+callback+"\" test/"+module_name+":latest bash")

def set_sdk_home(sdk_home,env_file):
    print("Don't forget to source you environment file after running this command!")
    if exists(env_file):
        output = ""
        text_file = open(env_file, "r")
        data = text_file.read()
        text_file.close()
        lines = data.split('\n')
        found = 0
        for line in lines:
            if line[0:19] == "export KB_SDK_HOME=":
                found = 1
                line = "export KB_SDK_HOME=\""+sdk_home+"\""
            output += line+"\n"
        if found == 0:
            output += "export KB_SDK_HOME=\""+sdk_home+"\""
        text_file = open(env_file, "w")
        text_file.write(output)
        text_file.close()

def activate_callback_server(sdk_home = None):
    if sdk_home == None:
        sdk_home = os.environ['KB_SDK_HOME']
    os.system("kb-sdk run chenry_utility_module.activate_callback_server -j '{}' -h "+sdk_home)
        
def stop_callback_server(sdk_home = None):
    if sdk_home == None:
        sdk_home = os.environ['KB_SDK_HOME']
    os.system("touch "+sdk_home+"/run_local/workdir/__DONE__")

my_parser = argparse.ArgumentParser(description='Run one or more SDK utilities')
my_parser.add_argument('Command',
    type=str,
    choices=["home","startcb","debug","stopcb"],
    help='select the command to be run')
if len(sys.argv) <= 2:  
    args = my_parser.parse_args()
#Further augmenting CLI based on command selected
if sys.argv[1] == "home":
    my_parser.add_argument('sdkhome',
        type=str,
        help='SDK home directory')
    my_parser.add_argument('envfile',
        type=str,
        default=None,
        help='environment file (e.g. ~/.bash_profile')
    args = my_parser.parse_args()
    set_sdk_home(args.sdkhome,args.envfile)
elif sys.argv[1] == "startcb":
    my_parser.add_argument('--sdkhome',
        type=str,
        default=None,
        help='SDK home (defaults to KB_SDK_HOME)')
    args = my_parser.parse_args()
    activate_callback_server(args.sdkhome)
elif sys.argv[1] == "debug":
    my_parser.add_argument('Module',
        type=str,
        help='directory of module to debug')
    my_parser.add_argument('--sdkhome',
        type=str,
        default=None,
        help='SDK home (defaults to KB_SDK_HOME)')
    my_parser.add_argument('--port',
        type=str,
        default=None,
        help='port for jupyter notebook (defaults to 8888)')
    args = my_parser.parse_args()
    debug_module(args.Module,args.sdkhome,args.port)
elif sys.argv[1] == "stopcb":
    my_parser.add_argument('--sdkhome',
        type=str,
        default=None,
        help='SDK home (defaults to KB_SDK_HOME)')
    args = my_parser.parse_args()
    stop_callback_server(args.sdkhome)