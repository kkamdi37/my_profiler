#!/usr/bin/env python3

import sys
import json
import xmltodict
import subprocess

def run_command( command ):
    cmd_proc = subprocess.Popen(  command, stdout=subprocess.PIPE
                                , stderr=subprocess.PIPE )
    return cmd_proc.communicate()[0]

def main():
    command = ['nvidia-smi', '--xml-format', '--query']
    bresult = run_command( command )
    str_result = bresult.decode( 'utf-8' )
    result = xmltodict.parse( str_result )

    print( json.dumps(result, sort_keys=True, indent=4) )

    return 0

if __name__ == "__main__":
    main()
