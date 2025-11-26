#!/usr/bin/env python3

import sys
import json
import time
import datetime
import xmltodict
import subprocess

def run_command( command ):
    cmd_proc = subprocess.Popen(  command, stdout=subprocess.PIPE
                                , stderr=subprocess.PIPE )
    return cmd_proc.communicate()[0]

def print_tabulate( table ):
    from tabulate import tabulate

    print( tabulate(table, headers='firstrow', tablefmt='fancy_grid') )
    return 0

def main():
    Loop = True
    interval = 60

    command = ['nvidia-smi', '--xml-format', '--query']
    nv_dt_fmt = "%a %b %d %H:%M:%S %Y"

    time.sleep( interval - time.time() % interval )

    while Loop:
        bresult = run_command( command )
        xml_result = xmltodict.parse( bresult.decode( 'utf-8' ) )

        result = xml_result["nvidia_smi_log"]
        gpu_info = result["gpu"]
        ts = datetime.datetime.strptime( result["timestamp"], nv_dt_fmt )
        #print( json.dumps(result, sort_keys=True, indent=4) )

        gpu_table = list()
        gpu_table.append( ["@id", "gpu_ut", "mem_ut", "pid", "used_mem"] )

        for i in range( len(gpu_info) ):
            #print( gpu_info[i]["@id"], gpu_info[i]["utilization"], gpu_info[i]["processes"] )

            tmp = list()
            tmp.append( gpu_info[i]["@id"] )
            tmp.append( gpu_info[i]["utilization"]["gpu_util"] )
            tmp.append( gpu_info[i]["utilization"]["memory_util"] )

            type_gpu_proc_info = type(gpu_info[i]["processes"]["process_info"])
            if type_gpu_proc_info is dict:
                tmp.append( gpu_info[i]["processes"]["process_info"]["pid"] )
                tmp.append( gpu_info[i]["processes"]["process_info"]["used_memory"] )
            elif type_gpu_proc_info is list:
                gi_pid_list = list()
                gi_usedmem_list = list()
                for gi in gpu_info[i]["processes"]["process_info"]:
                    if not gi["pid"] in gi_pid_list:
                        gi_pid_list.append(gi["pid"])
                        gi_usedmem_list.append(gi["used_memory"])
                tmp.append( ','.join(gi_pid_list) )
                tmp.append( ','.join(gi_usedmem_list) )
            gpu_table.append( tmp )

        print( "\n - Datetime: " + ts.strftime("%Y-%m-%d %H:%M:%S") )
        print_tabulate( gpu_table )

        time.sleep( interval - time.time() % interval)

    return 0

if __name__ == "__main__":
    main()
