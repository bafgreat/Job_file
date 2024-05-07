from __future__ import print_function
import sys
import subprocess
import os
import csv
import json, codecs
import numpy as np
path = os.getenv("HOME") + '/src/Job_file'
sys.path.append(path)

def Numpy_to_Json(Array, file_name):
    json.dump(Array.tolist(), codecs.open(file_name, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True)
    return
    
def Write_Json(list,file_name):
    json.dump(list, codecs.open(file_name, 'w', encoding='utf-8'))
    
    
def Json_to_Numpy(json_file):
    read_json = codecs.open(json_file, 'r', encoding='utf-8').read()
    read_json = np.array(json.loads(read_json))
    return read_json
    
def Read_Json(file_name):
    f = open(file_name)
    data = json.load(f)
    f.close()
    return data

def get_section(contents, start_key, stop_key, start_offset=0, stop_offset=0):
    all_start_indices = []
    for i, line in enumerate(contents):
        if  start_key in line:
            all_start_indices.append(i + start_offset)
    start_index = all_start_indices[-1]
    for i in range(start_index, len(contents)):
        line = contents[i]
        if stop_key in line:
            stop_index = i + 1 + stop_offset
            break
    data = contents[start_index:stop_index]
    return  data

def CSV_reader(file):
    f = open(file, 'r')
    data = csv.reader(f)
    return data

def get_contents(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()
    return contents

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return


