#!/usr/bin/env python
SLEEP_SECS = 3
SLEEP_SECS_BEFORE_SIZE_CALC = 30
LOG_DIR_SIZE_THRESHOLD = 1024 * 1024 * 1

import colorama, os, shutil, signal, subprocess, time, traceback
ZK_CLI= '/zk/bin/zkCli.sh'
ZK_SERVER = '/zk/bin/zkServer.sh'
ZK_LOG_FILE = 'zk.log'

def zk_conf_dir(i): return '/zk%02d_conf' % i

def zk_data_dir(i): return '/zk%02d_data' % i

def zk_log_dir(i): return '/zk%02d_log' % i

def zk_accepted_epoch_file(i): return os.path.join(zk_data_dir(i), 'version-2/acceptedEpoch')

def zk_current_epoch_file(i): return os.path.join(zk_data_dir(i), 'version-2/currentEpoch')

def read_int_from_file(fname):
    with open(fname, 'r') as f: i = int(f.read())
    return i

def zk_accepted_epoch(i): return read_int_from_file(zk_accepted_epoch_file(i))

def zk_current_epoch(i): return read_int_from_file(zk_current_epoch_file(i))
                                                   
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

def reset_zk_conf_dir(i): reset_dir(zk_conf_dir(i))

def reset_zk_data_dir(i): reset_dir(zk_data_dir(i))

def reset_zk_dirs(i):
    reset_zk_conf_dir(i)
    reset_zk_data_dir(i)

def run_zkcli(i, cmd):
    port = 2180 + i
    l = [ZK_CLI, '-server', 'localhost:%d' % port]
    l.extend(cmd.split())
    subprocess.call(l)

def run_nc_stat(i):
    port = 2180 + i
    cmd = 'echo stat | nc localhost %d' % port
    print(cmd)
    subprocess.call(cmd, shell=True)

def start_zkserver(i):
    env = dict(os.environ,
               ZOO_LOG_DIR=zk_log_dir(i),
               ZOO_LOG_FILE=ZK_LOG_FILE,
               ZOO_LOG4J_PROP='DEBUG,ROLLINGFILE')
    subprocess.call([ZK_SERVER, '--config', zk_conf_dir(i), 'start'],
                    env=env)
    pid_file_path = os.path.join(zk_data_dir(i), 'zookeeper_server.pid')
    pid = read_int_from_file(pid_file_path)
    return pid

def kill_proc(pid): os.kill(pid, signal.SIGKILL)

def INFO(message): print(colorama.Back.BLUE + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)

def ERROR(message): print(colorama.Back.RED + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    
def sleep(secs=SLEEP_SECS): INFO('* Sleeping for %d seconds' % secs); time.sleep(secs)

def show_stats(ids):
    for i in ids: run_nc_stat(i)
    for i in ids: print('acceptedEpoch(%d)=%d, currentEpoch(%d)=%d' % (i, zk_accepted_epoch(i), i, zk_current_epoch(i)))
        
INFO('Reproducing the bug: "infinite exception loop occurs when dataDir is lost"')
try:
    INFO('* Resetting')
    reset_zk_dirs(1); reset_zk_dirs(2)

    INFO('* Starting [1,2] with the initial ensemble [1]')
    pid1, pid2 = start_zkserver(1), start_zkserver(2)
    show_stats((1, 2))

    sleep()
    show_stats((1, 2))

    INFO('* Invoking Reconfig [1]->[2]')
    run_zkcli(1, 'reconfig -members server.2=127.0.0.1:2889:3889;2182')
    show_stats((1, 2))

    sleep()    
    show_stats((1, 2))
    assert zk_accepted_epoch(1) == zk_accepted_epoch(2) and \
        zk_current_epoch(1) == zk_current_epoch(2) and \
        zk_current_epoch(1) == zk_accepted_epoch(1) and \
        zk_current_epoch(1) == 2, 'Note: expecting acceptedEpoch(i)==currentEpoch(i)==2 for i = 1, 2 here.'
    
    INFO('* Killing server.2 (pid=%d)' % pid2)
    kill_proc(pid2)
    show_stats((1, 2))

    sleep()
    show_stats((1, 2))
    
    INFO('* Resetting %s' % zk_data_dir(2))
    ## Note: just removing {accepted,current}Epoch cannot reproduce the bug
    ## Note: in real environment, zk_conf_dir may be also removed due to reprovisioning.
    ##       so you can also add reset_zk_conf_dir(2) here.
    reset_zk_data_dir(2)
    
    INFO('* Starting server.2')
    pid2 = start_zkserver(2)
    show_stats((1, 2))
    
    sleep(secs=SLEEP_SECS_BEFORE_SIZE_CALC)
    show_stats((1, 2))
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
        INFO('NOTE: this container cannot always reproduce the bug due to non-determinism. Maybe you have to change SLEEP_SECS in this script.')
        INFO('AFAIK the bug can be reproduced with f5fb50ed2591ba9a24685a227bb5374759516828 (Apr 7, 2015).')
except Exception:
    ERROR('An error has occurred')
    ERROR(traceback.format_exc())
finally:
    INFO('* Exiting')
