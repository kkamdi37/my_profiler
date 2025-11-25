#!/usr/bin/env python3

import sys
import json
import datetime
import xmltodict
import subprocess

def run_command( command ):
    cmd_proc = subprocess.Popen(  command, stdout=subprocess.PIPE
                                , stderr=subprocess.PIPE )
    return cmd_proc.communicate()[0]

def main():
    command = ['nvidia-smi', '--xml-format', '--query']
    nv_dt_format = "%a %b %d %H:%M:%S %Y"


    bresult = run_command( command )
    str_result = bresult.decode( 'utf-8' )
    xml_result = xmltodict.parse( str_result )
    result = xml_result["nvidia_smi_log"]
    gpu_info = result["gpu"]

    ts = datetime.datetime.strptime( result["timestamp"], nv_dt_format )

    for i in range( len(gpu_info) ):
        print( gpu_info[i]["@id"], gpu_info[i]["utilization"], gpu_info[i]["processes"] )

    #print( json.dumps(result, sort_keys=True, indent=4) )

    return 0

if __name__ == "__main__":
    main()
