#!/usr/bin/python3

import os
import sys

architecture_dict = {1 : "32 bits", 2 : "64 bits"}

endianess_dict = {1 : "big endian", 2 : "little endian"}

abi_dict = {0 : "system V", 1 : "HP-UX", 2 : "NetBSD", 3 : "Linux", 4 : "GNU Hurd", 6 : "Solaris",\
	7 : "AIX", 8 : "IRIX", 9 : "FreeBSD", 0x0a : "Tru64", 0x0b : "Novell", 0x0c : "OpenBSD", 0x0d : "OpenVMS",\
	0x0e : "NonStop Kernel", 0x0f : "Aros", 0x10 : "FenixOS", 0x11 : "Nuxi", 0x12 : "OpenVOS"}

object_type_dict = {0 : "unknown", 1 : "relocatable", 2 : "executable", 3 : "shared object", 4 : "core file"}

machine_type_dict = {0x00: "No specific instruction set", 0x01: "AT&T WE 32100", 0x02: "SPARC", 0x03: "x86", 0x04: "Motorola 68000 (M68k)", 0x05: "Motorola 88000 (M88k)", 0x06: "Intel MCU", 0x07: "Intel 80860", 0x08: "MIPS", 0x09: "IBM System/370", 0x0A: "MIPS RS3000 Little-endian", 0x0F: "Hewlett-Packard PA-RISC", 0x13: "Intel 80960", 0x14: "PowerPC", 0x15: "PowerPC (64-bit)", 0x16: "S390, including S390x", 0x17: "IBM SPU/SPC", 0x24: "NEC V800", 0x25: "Fujitsu FR20", 0x26: "TRW RH-32", 0x27: "Motorola RCE", 0x28: "Arm (up to Armv7/AArch32)", 0x29: "Digital Alpha", 0x2A: "SuperH", 0x2B: "SPARC Version 9", 0x2C: "Siemens TriCore embedded processor", 0x2D: "Argonaut RISC Core", 0x2E: "Hitachi H8/300", 0x2F: "Hitachi H8/300H", 0x30: "Hitachi H8S", 0x31: "Hitachi H8/500", 0x32: "IA-64", 0x33: "Stanford MIPS-X", 0x34: "Motorola ColdFire", 0x35: "Motorola M68HC12", 0x36: "Fujitsu MMA Multimedia Accelerator", 0x37: "Siemens PCP", 0x38: "Sony nCPU embedded RISC processor", 0x39: "Denso NDR1 microprocessor", 0x3A: "Motorola Star*Core processor", 0x3B: "Toyota ME16 processor", 0x3C: "STMicroelectronics ST100 processor", 0x3D: "Advanced Logic Corp. TinyJ embedded processor family", 0x3E: "AMD x86-64", 0x3F: "Sony DSP Processor", 0x40: "Digital Equipment Corp. PDP-10", 0x41: "Digital Equipment Corp. PDP-11", 0x42: "Siemens FX66 microcontroller", 0x43: "STMicroelectronics ST9+ 8/16 bit microcontroller", 0x44: "STMicroelectronics ST7 8-bit microcontroller", 0x45: "Motorola MC68HC16 Microcontroller", 0x46: "Motorola MC68HC11 Microcontroller", 0x47: "Motorola MC68HC08 Microcontroller", 0x48: "Motorola MC68HC05 Microcontroller", 0x49: "Silicon Graphics SVx", 0x4A: "STMicroelectronics ST19 8-bit microcontroller", 0x4B: "Digital VAX", 0x4C: "Axis Communications 32-bit embedded processor", 0x4D: "Infineon Technologies 32-bit embedded processor", 0x4E: "Element 14 64-bit DSP Processor", 0x4F: "LSI Logic 16-bit DSP Processor", 0x8C: "TMS320C6000 Family", 0xAF: "MCST Elbrus e2k", 0xB7: "Arm 64-bits (Armv8/AArch64)", 0xDC: "Zilog Z80", 0xF3: "RISC-V", 0xF7: "Berkeley Packet Filter", 0x101: "WDC 65C816"}

p_type_dict = {0 : "PT_NULL", 1 : "PT_LOAD", 2 : "PT_DYNAMIC", 3 : "PT_INTERP", 4 : "PT_NOTE", 5 : "PT_SHLIB", 6 : "PT_PHDR",\
	7 : "PT_TLS", 0x60000000 : "PT_LOOS", 0x6474e550 : "PT_GNU_EH_FRAME", 0x6474e551 : "PT_GNU_STACK", 0x6474e552 : "PT_GNU_RELRO",\
	0x6FFFFFFF : "PT_HIOS", 0x70000000 : "PT_LOPROC", 0x7FFFFFFF : "PT_HIPROC"}

sh_type_dict = {0 : "SHT_NULL", 1 : "SHT_PROGBITS", 2 : "SHT_SYMTAB", 3 : "SHT_STRTAB", 4 : "SHT_RELA", 5 : "SHT_HASH", 6 : "SHT_DYNAMIC", 7 : "SHT_NOTE", 8 : "SHT_NOBITS", 9 : "SHT_REL", 0xa : "SHT_SHLIB", 0x0b : "SHT_DYNSYM", 0x0e : "SHT_INIT_ARRAY", 0x0f : "SHT_FINI_ARRAY", 0x10 : "SHT_PREINIT_ARRAY", 0x11 : "SHT_GROUP", 0x12 : "SHT_SYMTAB_SHNDX", 0x13 : "SHT_NUM", 0x60000000 : "SHT_LOOS"}

def get_dict_entry(dictionnary, key, category):
	try:
		return dictionnary[key]
	except KeyError:
		return f"unknown {category}"

def ei_class_get_archi_size(ei_class):
	return get_dict_entry(architecture_dict, ei_class, "architecture")

def ei_data_get_endianness(ei_data):
	return get_dict_entry(endianess_dict, ei_data, "endianness")

def ei_data_get_abi(ei_osabi):
	return get_dict_entry(abi_dict, ei_osabi, "abi")

def ei_get_type(elf_type):
	return get_dict_entry(object_type_dict, elf_type, "object type")

def e_get_machine(elf_machine):
	return get_dict_entry(machine_type_dict, elf_machine, "machine type")

def parse_elf_header(elfarray):

	e_ident = elfarray[:16]
	ei_mag = e_ident[:4]
	ei_class = e_ident[4]
	ei_data = e_ident[5]
	ei_version = e_ident[6]
	ei_osabi = e_ident[7]
	ei_abiversion = e_ident[8]
    
	print(f"e_ident :\t\t{e_ident}")
	print(f"ei_mag :\t\t{ei_mag}")
	print(f"ei_class :\t{ei_class} ({ei_class_get_archi_size(ei_class)})")
	print(f"ei_data :\t\t{ei_data} ({ei_data_get_endianness(ei_data)})")
	print(f"version :\t\t{ei_version}")
	print(f"ABI :\t\t\t{ei_osabi} ({ei_data_get_abi(ei_osabi)})")
	print(f"ABI version :\t{ei_abiversion}")

	e_type = int.from_bytes(elfarray[16:18], 'little')
	e_machine = int.from_bytes(elfarray[18:20], 'little')
	e_version = int.from_bytes(elfarray[20:24], 'little')
	e_entry = int.from_bytes(elfarray[24:32], 'little')
	e_phoff = int.from_bytes(elfarray[32:40], 'little')
	e_shoff = int.from_bytes(elfarray[40:48], 'little')

	e_flags = elfarray[48:52]
	
	e_ehsize = int.from_bytes(elfarray[52:54], 'little')
	e_phentsize = int.from_bytes(elfarray[54:56], 'little')
	e_phnum  = int.from_bytes(elfarray[56:58], 'little')
	e_shentsize = int.from_bytes(elfarray[58:60], 'little')
	e_shnum = int.from_bytes(elfarray[60:62], 'little')
	e_shstrndx = int.from_bytes(elfarray[62:64], 'little')


	print(f"e_type :\t\t{e_type} ({ei_get_type(e_type)})")
	print(f"e_machine :\t{e_machine} ({e_get_machine(e_machine)})")
	print(f"Version :\t\t{e_version}")
	print(f"Point d'entrée : \t\t{hex(e_entry)} ({e_entry})")
	print(f"Offset program header : \t{hex(e_phoff)} ({e_phoff})")
	print(f"Adresse en-tête de section : \t{hex(e_shoff)} ({e_shoff})")

	print(f"Flags file header : \t\t{e_flags}")
	print(f"Taille file header : \t\t{hex(e_ehsize)} ({e_ehsize})")

	print(f"Taille entrée program header :  {e_phentsize} octets")
	print(f"Nombre entrées program header : {e_phnum} entrées")

	print(f"Taille entrée section header :  {e_shentsize} octets")
	print(f"Nombre entrées section header : {e_shnum} entrées")
	print(f"Index du nom de section : \t{e_shstrndx}")

	return (e_phoff, e_phentsize, e_phnum, e_shoff, e_shentsize, e_shnum, e_shstrndx)

def parse_p_type(p_type):
	return get_dict_entry(p_type_dict, int.from_bytes(p_type, 'little'), "p_type")

def parse_p_flags(flags):
	flags_meaning = ""
	
	if flags & 0x04:
		flags_meaning += "R"
	if flags & 0x02:
		flags_meaning += "W"
	if flags & 0x01:
		flags_meaning += "X"
	return flags_meaning
	
def parse_elf_program_header_entry(program_header_entry):

	p_type = program_header_entry[0:4]
	p_flags = int.from_bytes(program_header_entry[4:8], 'little')
	p_offset = int.from_bytes(program_header_entry[8:16], 'little')
	p_vaddr = int.from_bytes(program_header_entry[16:24], 'little')
	p_paddr = int.from_bytes(program_header_entry[24:32], 'little')
	p_filesz = int.from_bytes(program_header_entry[32:40], 'little')
	p_memsz = int.from_bytes(program_header_entry[40:48], 'little')
	p_align = int.from_bytes(program_header_entry[48:56], 'little')

	segment_printable_entry = f"{parse_p_type(p_type):<8}\t\t{parse_p_flags(p_flags)}\t{hex(p_offset)}\t{hex(p_vaddr)}\t\t{hex(p_paddr)}\t{hex(p_filesz)}\t{hex(p_memsz)}\t{hex(p_align)}"

	return (parse_p_type(p_type), p_offset, segment_printable_entry)

def parse_sh_type(sh_type):
	return get_dict_entry(sh_type_dict, sh_type, "sh_type")

def parse_sh_flags(flags):
	flags_meaning = ""	

	if flags & 0x01:
		flags_meaning += "W"
	if flags & 0x02:
		flags_meaning += "A"
	if flags & 0x04:
		flags_meaning += "X"
	if flags & 0x10:
		flags_meaning += "M"
	if flags & 0x20:
		flags_meaning += "S"
	if flags & 0x40:
		flags_meaning += "I"
	if flags & 0x80:
		flags_meaning += "L"
	if flags & 0x100:
		flags_meaning += "O"
	if flags & 0x200:
		flags_meaning += "G"
	if flags & 0x400:
		flags_meaning += "T"
	if flags & 0x0FF00000:
		flags_meaning += "o"
	if flags & 0xF0000000:
		flags_meaning += "p"
	return flags_meaning

def read_string_at(array, offset):

	index = offset
	c = array[index]
	while c != 0:
		index += 1
		c = array[index]

	name = array[offset:index]
	return str(name)

def get_section_name(elfarray, section_name_entry_offset, sh_name):
	section_name = read_string_at(elfarray, section_name_entry_offset + sh_name)
	return section_name

def parse_elf_section_header_entry(elfarray, section_header_entry, section_name_entry_offset):

	sh_name = int.from_bytes(section_header_entry[0:4], 'little')
	sh_type = int.from_bytes(section_header_entry[4:8], 'little')
	sh_flags = int.from_bytes(section_header_entry[8:16], 'little')
	sh_addr = int.from_bytes(section_header_entry[16:24], 'little')
	sh_offset = int.from_bytes(section_header_entry[24:32], 'little')
	sh_size = int.from_bytes(section_header_entry[32:40], 'little')
	sh_link = int.from_bytes(section_header_entry[40:44], 'little')
	sh_info = int.from_bytes(section_header_entry[44:48], 'little')
	sh_addralign = int.from_bytes(section_header_entry[48:56], 'little')
	sh_entsize = int.from_bytes(section_header_entry[56:64], 'little')

	section_name = get_section_name(elfarray, section_name_entry_offset, sh_name)

	section_printable_entry = f"{hex(sh_name)}\t\t{section_name:<16}\t{parse_sh_type(sh_type)}\t{parse_sh_flags(sh_flags)}\t{hex(sh_addr)}\t{hex(sh_offset)}\t{hex(sh_size)}\t{hex(sh_link)}\t{hex(sh_info)}\t{hex(sh_addralign)}\t{hex(sh_entsize)}"

	return (section_name, sh_offset, section_printable_entry)

def parse_elf_program_header(elfarray, e_phoff, e_phentsize, e_phnum):

	segment_list = []
	print("n°\ttype\t\t\tflags\toffset\tvaddr\t\tpaddr\tfilesz\tmemsz\talign")

	for i in range(e_phnum):
		program_header_entry = elfarray[e_phoff + i * e_phentsize : e_phoff + i * e_phentsize + e_phentsize]
		(p_type, p_offset, parsed_elf_program_header_entry) = parse_elf_program_header_entry(program_header_entry)
		print(f"{i}\t{parsed_elf_program_header_entry}")

		segment_list.append([p_offset, p_type])

	segment_list = sort_segment_list(segment_list)
	return segment_list

def parse_elf_section_header(elfarray, e_shoff, e_shentsize, e_shnum, e_shstrndx):

	section_list = []
	print("n°\toffset_name\tname\t\t\ttype\t\tflags\tvaddr\toffset\tsize\tlink\tinfo\talign\tentsize")

	section_header_name_entry = elfarray[e_shoff + e_shstrndx * e_shentsize : e_shoff + e_shstrndx * e_shentsize + e_shentsize]
	section_name_entry_offset = int.from_bytes(section_header_name_entry[24:32], 'little')

	for i in range(e_shnum):
		section_header_entry = elfarray[e_shoff + i * e_shentsize : e_shoff + i * e_shentsize + e_shentsize]
		(section_name, sh_offset, parsed_section_header_entry) = parse_elf_section_header_entry(elfarray, section_header_entry, section_name_entry_offset)
		print(f"{i}\t{parsed_section_header_entry}")
		
		section_list.append([sh_offset, section_name])

	return section_list

def parse_elf(elfarray):
	(e_phoff, e_phentsize, e_phnum, e_shoff, e_shentsize, e_shnum, e_shstrndx) = parse_elf_header(elfarray)
	segment_list = parse_elf_program_header(elfarray, e_phoff, e_phentsize, e_phnum)
	print("")
	section_list = parse_elf_section_header(elfarray, e_shoff, e_shentsize, e_shnum, e_shstrndx)

	m = len(segment_list)
	n = len(section_list)

	i = 0 
	j = 0

	while (i < m) or (j < n):
		
		print(f"segment {i} : {segment_list[i][0]} : {segment_list[i][1]}", end = '')
		
		curr_seg_addr = segment_list[i][0]
		
		if i < m -1:
			next_seg_addr = segment_list[i + 1][0]
		else:
			next_seg_addr = 9999999999999999999999
		
		curr_sec_addr = section_list[j][0]
		
		while (curr_sec_addr < next_seg_addr) and (j < n):
			
			if curr_sec_addr == curr_seg_addr:
				print(f"\tsection {j} : {section_list[j][0]} : {section_list[j][1]}")
			else:
				print(f"\t\t\t\t\tsection {j} : {section_list[j][0]} : {section_list[j][1]}")
			j += 1
			if j < n:
				curr_sec_addr = section_list[j][0]
		i += 1
		print("")

def sort_segment_list(segment_list):

	n = len(segment_list)
	for i in range(n):
		for j in range(n - i - 1):
			if (segment_list[j][0] > segment_list[j + 1][0]):
				tmp = segment_list[j]
				segment_list[j] = segment_list[j + 1]
				segment_list[j + 1] = tmp

	return segment_list

def main(args):
	elfpath = args[1]
    
	elfsize = os.stat(elfpath).st_size
    
	with open(elfpath, "rb") as fd:
		elfarray = fd.read(elfsize)


	parse_elf(elfarray)

if __name__ == '__main__':
	main(sys.argv)
