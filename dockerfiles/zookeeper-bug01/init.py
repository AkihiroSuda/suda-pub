#!/usr/bin/env python
SLEEP_SECS_BEFORE_SIZE_CALC = 30
LOG_DIR_SIZE_THRESHOLD = 1024 * 1024 * 10

import colorama, os, shutil, signal, subprocess, time, traceback

ZK_CLI= '/zk/bin/zkCli.sh'
ZK_SERVER = '/zk/bin/zkServer.sh'
ZK_LOG_FILE = 'zk.log'

def zk_conf_dir(i):
    assert i > 0
    return '/zk%02d_conf' % i

def zk_data_dir(i):
    assert i > 0
    return '/zk%02d_data' % i

def zk_log_dir(i):
    assert i > 0
    return '/zk%02d_log' % i

def get_dir_size(d):
    s = 0
    for dirpath, dirnames, filenames in os.walk(d):
        for f in filenames:
            path = os.path.join(dirpath, f)
            s += os.path.getsize(path)
    return s

def reset_dir(d, orig_d=None):
    if not orig_d: orig_d = d + '.ORIG'
    if os.path.isdir(d): shutil.rmtree(d)
    shutil.copytree(orig_d, d)

def reset_zk_conf_dir(i):
    assert i > 0
    reset_dir(zk_conf_dir(i))

def reset_zk_data_dir(i):
    assert i > 0
    reset_dir(zk_data_dir(i))

def reset_zk_dirs(i):
    reset_zk_conf_dir(i)
    reset_zk_data_dir(i)

def run_zkcli(i, cmd):
    assert i > 0
    port = 2180 + i
    l = [ZK_CLI, '-server', 'localhost:%d' % port]
    l.extend(cmd.split())
    subprocess.call(l)

def run_nc_stat(i):
    assert i > 0
    port = 2180 + i
    os.system('echo stat | nc localhost %d' % port)

def start_zkserver(i):
    assert i > 0
    env = dict(os.environ,
               ZOO_LOG_DIR=zk_log_dir(i),
               ZOO_LOG_FILE=ZK_LOG_FILE,
               ZOO_LOG4J_PROP='INFO,ROLLINGFILE')
    subprocess.call([ZK_SERVER, '--config', zk_conf_dir(i), 'start'],
                    env=env)
    pid_file_path = os.path.join(zk_data_dir(i), 'zookeeper_server.pid')
    with open(pid_file_path, 'r') as f: pid = int(f.read())
    return pid

def kill_proc(pid):
    assert pid > 0
    os.kill(pid, signal.SIGKILL)

def INFO(message):
    print(colorama.Back.BLUE + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)

def ERROR(message):
    print(colorama.Back.RED + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    
def drop_to_shell():
    os.system('/bin/bash --login -i')
    
def prompt(message='Press RET to continue or type "shell" to drop to shell'):
    while True:
        input = raw_input(colorama.Back.BLUE + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
        if input == 'shell': drop_to_shell()
        if input in ('', 'y', 'yes'): break

        
INFO('Reproducing the bug: "A specific order of reconfig and crash/restart with a badly rolled-back conf leads to infinite exception loop"')
try:    
    INFO('Resetting..'); prompt()
    reset_zk_dirs(1)
    reset_zk_dirs(2)

    INFO('Starting [1,2] with the initial ensemble [1]'); prompt()
    pid1 = start_zkserver(1)
    pid2 = start_zkserver(2)
    run_nc_stat(1)
    run_nc_stat(2)

    INFO('Invoking Reconfig [1]->[1,2]'); prompt()
    run_zkcli(1, 'reconfig -add server.2=127.0.0.1:2889:3889;2182')
    run_nc_stat(1)
    run_nc_stat(2)

    INFO('Invoking Reconfig [1,2]->[2]'); prompt()
    run_zkcli(1, 'reconfig -remove 1')
    run_nc_stat(1)
    run_nc_stat(2)

    INFO('Killing server.2 (pid=%d)' % pid2); prompt()
    kill_proc(pid2)
    run_nc_stat(1)
    run_nc_stat(2)

    INFO('Resetting server.2 to the initial ensemble [2]'); prompt()
    reset_zk_dirs(2)

    INFO('Starting server.2'); prompt()
    pid2 = start_zkserver(2)
    run_nc_stat(1)
    run_nc_stat(2)

    INFO('Sleeping for %d seconds' % SLEEP_SECS_BEFORE_SIZE_CALC)
    time.sleep(SLEEP_SECS_BEFORE_SIZE_CALC)
    reproduced = False
    for i in (1, 2):
        dir_path = zk_log_dir(i)
        dir_size = get_dir_size(dir_path)
        INFO('%s: %d bytes' % (dir_path, dir_size))
        if dir_size > LOG_DIR_SIZE_THRESHOLD:
             INFO('The log dir is extremely large. Perhaps the bug was REPRODUCED!')
             reproduced = True
    if not reproduced:
        ERROR('The bug was not reproduced?')
        INFO('If the bug was not reproduced, please try to run this container several times.')
        INFO('NOTE: this container cannot always reproduce the bug due to non-determinism.')
        INFO('AFAIK the bug can be reproduced with f5fb50ed2591ba9a24685a227bb5374759516828 (Apr 7, 2015).')
except Exception:
    ERROR('An error has occurred')
    ERROR(traceback.format_exc())
finally:
    INFO('Dropping to shell..')
    drop_to_shell()
    INFO('Exiting..')
