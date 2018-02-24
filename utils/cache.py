#!/usr/bin/python3
# coding=utf-8
# © 2017 Master
# This code is covered under GPLv2+, see LICENSE
#####################

#import global_module as g
import pathlib

class Cache:
    def __init__(self, path):
        filename = path + "gom64p.cache"
        self.cache_fn = pathlib.Path(filename).resolve()
        self.cache = []
        self.version = None
        self.recent_files = None
        self.total_roms = None
        self.date = None
        self.generated_list = None

        if self.cache_fn.is_file() == True and self.cache_fn.exists() == True:
            self.read_cache()
        else:
            print("cache file not found.")
            self.create_cache()
            self.read_cache()


    def create_cache(self):
        print("Creating new cache...")
        with open(self.cache_fn, 'w') as file:
            file.write("0\n")    #1, version
            file.write("\n")     #2
            file.write("# Recent files\n")     #3
            file.write("[]\n")   #4 recent_files
            file.write("\n")     #5
            file.write("# Number of roms\n")     #6
            file.write("0\n")     #7 total_roms
            file.write("# Date last generation\n")     #8
            file.write("0\n")     #9 date
            file.write("# Generated rom list\n")     #10
            file.write("[]\n")   #11 generated_list

    def read_cache(self):
        print("Reading cache...")
        with open(self.cache_fn, 'r') as file:
            # read a list of lines into data
            self.cache = file.readlines()
        self.version = self.cache[0].rstrip('\n')
        self.recent_files = self.cache[3].rstrip('\n')
        self.total_roms = self.cache[6].rstrip('\n')
        self.date = self.cache[8].rstrip('\n')
        self.generated_list = self.cache[10].rstrip('\n')

    def write_cache(self):
        print("Writing to cache...")
        self.cache[0] = self.version + '\n'
        self.cache[3] = str(self.recent_files) + '\n'
        self.cache[6] = self.total_roms + '\n'
        self.cache[8] = self.date + '\n'
        self.cache[10] = str(self.generated_list) + '\n'

        with open(self.cache_fn, 'w') as file:
            file.writelines(self.cache)



    
