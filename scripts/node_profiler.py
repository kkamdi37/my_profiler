#!/usr/bin/env python3

import sys
import psutil
import socket
import time
import datetime

def get_host_info():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname( host_name )
    return ( host_name, host_ip )

def get_proc_info( p, hnm, hip ):
    data = dict()

    # p.cputimes(user, system, children_user, children_system, iowait)
    data["cpu_time"] = sum( p.cpu_times()[:4] )

    # p.mem(rss, vms, shared, text, lib, data, dirty)
    data["mem_usage"] = p.memory_info()[0]

    # p.io(   read_count, write_count, read_bytes, write_bytes
    #       , read_chars, write_chars )
    (   data["io_r_count"], data["io_w_count"]
      , data["io_r_bytes"], data["io_w_bytes"]
      , data["io_r_chars"], data["io_w_chars"]
    ) = p.io_counters()

    # p.openfile(path, fd, position, mode, flags)
    open_accounts = list()
    fds = p.open_files()
    for fd in fds:
        if fd[0].startswith("/home/"):
            account = fd[0].split("/")[2]
            if not account in open_accounts:
                open_accounts.append( account )
    data["open_accnt"] = ','.join(open_accounts)

    # p.net_connections( fd, family, type, laddr, raddr, status )
    conn_hosts = list()
    for temp in p.net_connections():
        if temp[4]:
            if temp[4][0] != hip:
                connected_host = temp[4][0]
                if not connected_host in conn_hosts:
                    conn_hosts.append( connected_host )

    for child in p.children( recursive=True ):
        try:
            data["cpu_time"]  += sum( child.cpu_times()[:2] )
            data["mem_usage"] += child.memory_info()[0]

            (   data["io_r_count"], data["io_w_count"]
              , data["io_r_bytes"], data["io_w_bytes"]
              , data["io_r_chars"], data["io_w_chars"]
            ) = child.io_counters()

            fds = child.open_files()
            for fd in fds:
                if fd[0].startswith("/home/"):
                    account = fd[0].split("/")[2]
                    if not account in open_accounts:
                        open_accounts.append( account )

            for temp in child.net_connections():
                if temp[4]:
                    if temp[4][0] != hip:
                        connected_host = temp[4][0]
                        if not connected_host in conn_hosts:
                            conn_hosts.append( connected_host )

        except psutil.NoSuchProcess:
            print( f'No Such Process: {child}' )
            continue

    data["conn_hosts"] = ','.join( conn_hosts )

    return data

def main():
    pids = [ int(sys.argv[1]) ]
    interval = 60
    ( hostnm, hostip ) = get_host_info()

    #time.sleep( interval - time.time() % interval)

    while(True):
        timestamp = datetime.datetime.now()

        for pid in pids:
            if not psutil.pid_exists( pid ): continue

            p = psutil.Process( pid )
            crnt_data = get_proc_info( p, hostnm, hostip )

            print( f'[{timestamp}, {pid}] {crnt_data["cpu_time"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["mem_usage"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_r_count"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_w_count"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_r_bytes"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_w_bytes"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_r_chars"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["io_w_chars"]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["open_accnt"][:255]=}' )
            print( f'[{timestamp}, {pid}] {crnt_data["conn_hosts"][:255]=}\n' )

        time.sleep( interval - time.time() % interval)

if __name__ == "__main__":
    main()



# lshosts -o 'ncpus maxmem' --json ${hostname}
# objs='jobid stat user pids first_host nalloc_host submit_time start_time cpu_used mem swap'
# bjobs -u all -m ${hostname} -json -o ${objs}
#
# /usr/sbin/nfsiostat /home/${USER}
# /usr/bin/dd bs=1k count=1 conv=fdatasync if=/dev/zero /home/${USER}/.dd.test
# /usr/bin/rm -rf /home/${USER}/.dd.test
#
