#!/usr/bin/python3

import os
import sys

def parse_elf_header(elfarray):
    e_ident = elfarray[:16]
    ei_mag = e_ident[:4]
    ei_class = e_ident[4]
    ei_data = e_ident[5]
    ei_version = e_ident[6]    
    
    print("e_ident : %r" % e_ident)
    print("ei_mag : %r" % ei_mag)
    print("ei_class : %r" % ei_class)
    print("ei_data : %r" % ei_data)
    print("ei_version : %r" % ei_version)

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
