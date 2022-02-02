#!/usr/bin/python3

import os
import sys

def parse_elf_header(elfarray):

    e_ident = elfarray[:16]
    ei_mag = e_ident[:4]
    ei_class = e_ident[4]
    ei_data = e_ident[5]
    ei_version = e_ident[6]
    ei_osabi = e_ident[7]
    ei_abiversion = e_ident[8]
    
    print("e_ident :\t%r" % e_ident)
    print("ei_mag :\t%r" % ei_mag)
    print("ei_class :\t%r" % ei_class)
    print("ei_data :\t%r" % ei_data)
    print("ei_version :\t%r" % ei_version)
    print("ei_osabi :\t%r" % ei_osabi)
    print("ei_abiversion :\t%r" % ei_abiversion)

    e_type = elfarray[16:18]
    e_machine = elfarray[18:20]
    e_version = elfarray[20:24]

    print("e_type :\t%r" % e_type)
    print("e_machine :\t%r" % e_machine)
    print("e_version :\t%r" % e_version)

def parse_elf(elfarray):
    parse_elf_header(elfarray)

def main(args):
    elfpath = args[1]
    
    elfsize = os.stat(elfpath).st_size
    
    with open(elfpath, "rb") as fd:
        elfarray = fd.read(elfsize)
        
    #print(elfarray)

    parse_elf(elfarray)

if __name__ == '__main__':
	main(sys.argv)
