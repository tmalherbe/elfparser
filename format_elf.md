Ce document tente d'expliquer la structure d'un fichier ELF.

# Références

- https://en.wikipedia.org/wiki/Executable_and_Linkable_Format

- https://stevens.netmeister.org/631/elf.html

- man elf

- https://llvm.org/doxygen/BinaryFormat_2ELF_8h_source.html

- http://www.skyfree.org/linux/references/ELF_Format.pdf

- https://elixir.bootlin.com/linux/latest/source/arch/x86/include/asm/elf.h

# TL;DR

Si on est pressé on peut tout aussi bien regarder le magnifique schéma de Corkami :

https://upload.wikimedia.org/wikipedia/commons/e/e4/ELF_Executable_and_Linkable_Format_diagram_by_Ange_Albertini.png

# Le file header d'un fichier ELF

Les informations essentielles de l'en-tête ELF sont :

- `ei_class` et `e_machine` qui spécifient la taille (32 ou 64 bits) et le type de processeurs.
- `ei_osab`i qui décrit l'ABI.
- `e_entry`, adresse dans le fichier du point d'entrée.
- `e_phoff`, adresse dans le fichier de la table des program headers, tableau des en-têtes de segments. Chaque en-tête décrit un segment.
- `e_shoff`, adresse dans le fichier de la table des section headers, tableau similaire mais destiné à décrire les sections.
- `e_ehsize`, taille du présent en-tête de fichier ELF.
- `e_phentsize`, taille de chaque en-tête de segment.
- `e_phnum`, nombre d'entrées dans le tableau des en-têtes de segments.
- `e_shentsize`, taille des en-têtes de section.
- `e_shnum`, nombre d'en-têtes de section.
- `e_shstrndx`, index dans la table des en-têtes de section de l'entrée décrivant la section contenant les noms des autres sections (c'est généralement la dernière entrée).

On peut lister cet en-tête avec `readelf -h toto` ou `objdump -f ls`.

# Les program headers

Le tableau des en-têtes de program (de segment) est généralement situé juste après l'en-tête de fichier.
Ce tableau permet de décrire l'agencement de l'espace mémoire du programme lors de l'exécution.

Chaque entrée a le contenu suivant :

- `p_type` : Le type du segment.
- `p_flags` : Les droits positionnés sur le segment (Lecture/Ecriture/Exécution).
- `p_offset` : Adresse du segment dans le fichier.
- `p_vaddr` : Adresse du segment en mémoire virtuelle.
- `p_paddr` : Adresse du segment en mémoire physique (pour les systèmes où cette information est pertinente !).
- `p_filesz` : taille du segment dans le programme. Cette taille peut être nulle.
- `p_memsz` : Taille du segment en mémoire. Peut être nulle.
- `p_align` : Spécifie les contraintes d'alignement ; 0 : Pas d'alignement. Sinon, c'est une puissance de 2, et on doit avoir `p_vaddr` = `p_offset` mod `p_align`.

## Types de segments

- `PT_PHDR` : Le segment de ce type est la table des en-têtes de programme.
- `PT_INTERP` : Ce segment contient le chemin absolu de l'interpréteur, c'est-à-dire de l'éditeur de liens dynamique.
- `PT_LOAD` : Seul les segments de ce type seront effectivement chargés en mémoire !
- `PT_DYNAMIC` : Segment contenant des informations nécessaires à l'édition de lien dynamique.
- `PT_NOTE` : Segment contenant des notes.
- `PT_GNU_RELRO` : Décrit la localisation et la taille d'un segment qui est destiné à devenir read-only après relocalisation.

Ce segment n'est pas présent si le binaire est compilé sans relro :

```
$ gcc toto.c -o toto -O0 -Wl,-z,relro,-z,now ; readelf --segments ./toto -W | grep GNU_RELRO
  GNU_RELRO      0x002d98 0x0000000000003d98 0x0000000000003d98 0x000268 0x000268 R   0x1
$ gcc toto.c -o toto -O0 -Wl,-z,norelro ; readelf --segments ./toto -W | grep GNU_RELRO
$
```

- `PT_GNU_STACK` : Ce segment sert à préciser les droits sur la pile via `p_flags` : est-elle exécutable ?

On peut se convaincre du dernier point en compilant un programme normalement puis avec une pile exécutable :

```
$ gcc toto.c -o toto -O0 ; readelf --segments ./toto -W | grep GNU_STACK
  GNU_STACK      0x000000 0x0000000000000000 0x0000000000000000 0x000000 0x000000 RW  0x10
$ gcc toto.c -o toto -O0 -z execstack ; readelf --segments ./toto -W | grep GNU_STACK
  GNU_STACK      0x000000 0x0000000000000000 0x0000000000000000 0x000000 0x000000 RWE 0x10
```

On peut lister les segments avec `objdump -p ./toto` ou (mieux) `readelf -W --segments ./toto`.

# Les section headers

Le contenu du fichier est découpé en sections, ayant chacune un rôle spécifique et un contenu spécifique.

Chaque en-tête de section a le contenu suivant :

- `sh_name` : Offset du nom de la section actuelle, dans la section contenant le nom des sections.
- `sh_type` : Le type de section. Détaillé plus bas.
- `sh_flags` : Fournit diverses informations sur la section : Est-elle accessible en ecriture (`SHF_WRITE`), son contenu est-il mappé dans la mémoire à l'exécution (`SHF_ALLOC`).
- `sh_addr` : Si la section est mappée en mémoire à l'exécution, offset de la section dans la mémoire du processus. Zéro sinon.
- `sh_offset` : Offset de la section dans le fichier.
- `sh_size` : Taille de la section.
- `sh_link` : Signification variable suivant le type de section.
- `sh_info` : idem.
- `sh_addralign` : Contraintes d'alignement. On doit avoir `sh_addr` = 0 mod `sh_addralign`. Valeurs possibles : 0 ou 1 (pas de contrainte d'alignement) ou toute autre puissance de 2.
- `sh_entsize` : Spécifie la taille des entrées de la section (certaines sections sont des tableaux contenant des entrées de taille fixe). Vaut zéro si la section n'est pas un tableau d'entrées de taille fixe.

# Les sections qui sont des tableaux

Ce sont les sections dont l'en-tête de section a un champ `sh_entsize`non nul.

Compilons un .so de test et regardons quelles sont ces sections :

```
$ gcc dummylib.c -o dummylib.so -shared
$ python3 ./elfparse.py ./dummylib.so
(...)
n°	offset_name	name							type					flags		vaddr		offset	size	link	info	align	entsize
0	0x0			b''             			SHT_NULL							0x0		0x0		0x0	0x0	0x0	0x0	0x0
1	0x1b			b'.note.gnu.build-id'	SHT_NOTE				A			0x238		0x238		0x24	0x0	0x0	0x4	0x0
2	0x2e			b'.gnu.hash'    			unknown sh_type	A			0x260		0x260		0x30	0x3	0x0	0x8	0x0
3	0x38			b'.dynsym'      			SHT_DYNSYM			A			0x290		0x290		0xd8	0x4	0x1	0x8	0x18
4	0x40			b'.dynstr'      			SHT_STRTAB			A			0x368		0x368		0x90	0x0	0x0	0x1	0x0
5	0x48			b'.gnu.version' 			unknown sh_type	A			0x3f8		0x3f8		0x12	0x3	0x0	0x2	0x2
6	0x55			b'.gnu.version_r'			unknown sh_type	A			0x410		0x410		0x20	0x4	0x1	0x8	0x0
7	0x64			b'.rela.dyn'    			SHT_RELA	A						0x430		0x430		0xa8	0x3	0x0	0x8	0x18
8	0x6e			b'.rela.plt'    			SHT_RELA	AI						0x4d8		0x4d8		0x18	0x3	0x15	0x8	0x18
9	0x78			b'.init'        			SHT_PROGBITS		AX			0x1000	0x1000	0x17	0x0	0x0	0x4	0x0
10	0x73			b'.plt'         			SHT_PROGBITS		AX			0x1020	0x1020	0x20	0x0	0x0	0x10	0x10
11	0x7e			b'.plt.got'     			SHT_PROGBITS		AX			0x1040	0x1040	0x8	0x0	0x0	0x8	0x8
12	0x87			b'.text'        			SHT_PROGBITS		AX			0x1050	0x1050	0x19e	0x0	0x0	0x10	0x0
13	0x8d			b'.fini'        			SHT_PROGBITS		AX			0x11f0	0x11f0	0x9	0x0	0x0	0x4	0x0
14	0x93			b'.rodata'      			SHT_PROGBITS		A			0x2000	0x2000	0x82	0x0	0x0	0x8	0x0
15	0x9b			b'.eh_frame_hdr'			SHT_PROGBITS		A			0x2084	0x2084	0x34	0x0	0x0	0x4	0x0
16	0xa9			b'.eh_frame'    			SHT_PROGBITS		A			0x20b8	0x20b8	0xbc	0x0	0x0	0x8	0x0
17	0xb3			b'.init_array'  			SHT_INIT_ARRAY		WA			0x3e10	0x2e10	0x8	0x0	0x0	0x8	0x8
18	0xbf			b'.fini_array'  			SHT_FINI_ARRAY		WA			0x3e18	0x2e18	0x8	0x0	0x0	0x8	0x8
19	0xcb			b'.dynamic'     			SHT_DYNAMIC			WA			0x3e20	0x2e20	0x1c0	0x4	0x0	0x8	0x10
20	0x82			b'.got'         			SHT_PROGBITS		WA			0x3fe0	0x2fe0	0x20	0x0	0x0	0x8	0x8
21	0xd4			b'.got.plt'     			SHT_PROGBITS		WA			0x4000	0x3000	0x20	0x0	0x0	0x8	0x8
22	0xdd			b'.data'        			SHT_PROGBITS		WA			0x4020	0x3020	0x8	0x0	0x0	0x8	0x0
23	0xe3			b'.bss'         			SHT_NOBITS			WA			0x4028	0x3028	0x8	0x0	0x0	0x1	0x0
24	0xe8			b'.comment'     			SHT_PROGBITS		MS			0x0		0x3028	0x27	0x0	0x0	0x1	0x1
25	0x1			b'.symtab'      			SHT_SYMTAB						0x0		0x3050	0x528	0x1a	0x2f	0x8	0x18
26	0x9			b'.strtab'      			SHT_STRTAB						0x0		0x3578	0x1c3	0x0	0x0	0x1	0x0
27	0x11			b'.shstrtab'    			SHT_STRTAB						0x0		0x373b	0xf1	0x0	0x0	0x1	0x0
```

Les sections `.dynsym`, `.gnu.version`, `.rela.dyn`, `.rela.plt`, `.plt`, `.plt.got`, `.init_array`, `.fini_array`, `.dynamic`, `.got`, `.got.plt`, `.comment` et `.symtab` sont des tableaux.

Notons que ni readelf ni objdump ne semble permettre de récupérer `entsize`.

# Compilation en mode débug

Si l'on compile en mode débug :

```
$ gcc dummylib.c -g -o dummylib_debug.so -shared
$ python3 ./elfparse.py ./dummylib_debug.so
(...)
n°	offset_name	name							type					flags		vaddr		offset	size	link	info	align	entsize
0	0x0			b''             			SHT_NULL							0x0		0x0		0x0	0x0	0x0	0x0	0x0
1	0x1b			b'.note.gnu.build-id'	SHT_NOTE				A			0x238		0x238		0x24	0x0	0x0	0x4	0x0
2	0x2e			b'.gnu.hash'    			unknown sh_type	A			0x260		0x260		0x30	0x3	0x0	0x8	0x0
3	0x38			b'.dynsym'      			SHT_DYNSYM			A			0x290		0x290		0xd8	0x4	0x1	0x8	0x18
4	0x40			b'.dynstr'      			SHT_STRTAB			A			0x368		0x368		0x90	0x0	0x0	0x1	0x0
5	0x48			b'.gnu.version' 			unknown sh_type	A			0x3f8		0x3f8		0x12	0x3	0x0	0x2	0x2
6	0x55			b'.gnu.version_r'			unknown sh_type	A			0x410		0x410		0x20	0x4	0x1	0x8	0x0
7	0x64			b'.rela.dyn'    			SHT_RELA				A			0x430		0x430		0xa8	0x3	0x0	0x8	0x18
8	0x6e			b'.rela.plt'    			SHT_RELA				AI			0x4d8		0x4d8		0x18	0x3	0x15	0x8	0x18
9	0x78			b'.init'        			SHT_PROGBITS		AX			0x1000	0x1000	0x17	0x0	0x0	0x4	0x0
10	0x73			b'.plt'         			SHT_PROGBITS		AX			0x1020	0x1020	0x20	0x0	0x0	0x10	0x10
11	0x7e			b'.plt.got'     			SHT_PROGBITS		AX			0x1040	0x1040	0x8	0x0	0x0	0x8	0x8
12	0x87			b'.text'        			SHT_PROGBITS		AX			0x1050	0x1050	0x19e	0x0	0x0	0x10	0x0
13	0x8d			b'.fini'        			SHT_PROGBITS		AX			0x11f0	0x11f0	0x9	0x0	0x0	0x4	0x0
14	0x93			b'.rodata'      			SHT_PROGBITS		A			0x2000	0x2000	0x82	0x0	0x0	0x8	0x0
15	0x9b			b'.eh_frame_hdr'			SHT_PROGBITS		A			0x2084	0x2084	0x34	0x0	0x0	0x4	0x0
16	0xa9			b'.eh_frame'    			SHT_PROGBITS		A			0x20b8	0x20b8	0xbc	0x0	0x0	0x8	0x0
17	0xb3			b'.init_array'  			SHT_INIT_ARRAY		WA			0x3e10	0x2e10	0x8	0x0	0x0	0x8	0x8
18	0xbf			b'.fini_array'  			SHT_FINI_ARRAY		WA			0x3e18	0x2e18	0x8	0x0	0x0	0x8	0x8
19	0xcb			b'.dynamic'     			SHT_DYNAMIC			WA			0x3e20	0x2e20	0x1c0	0x4	0x0	0x8	0x10
20	0x82			b'.got'         			SHT_PROGBITS		WA			0x3fe0	0x2fe0	0x20	0x0	0x0	0x8	0x8
21	0xd4			b'.got.plt'     			SHT_PROGBITS		WA			0x4000	0x3000	0x20	0x0	0x0	0x8	0x8
22	0xdd			b'.data'        			SHT_PROGBITS		WA			0x4020	0x3020	0x8	0x0	0x0	0x8	0x0
23	0xe3			b'.bss'         			SHT_NOBITS			WA			0x4028	0x3028	0x8	0x0	0x0	0x1	0x0
24	0xe8			b'.comment'     			SHT_PROGBITS		MS			0x0		0x3028	0x27	0x0	0x0	0x1	0x1
25	0xf1			b'.debug_aranges'			SHT_PROGBITS					0x0		0x304f	0x30	0x0	0x0	0x1	0x0
26	0x100			b'.debug_info'  			SHT_PROGBITS					0x0		0x307f	0x1a0	0x0	0x0	0x1	0x0
27	0x10c			b'.debug_abbrev'			SHT_PROGBITS					0x0		0x321f	0xac	0x0	0x0	0x1	0x0
28	0x11a			b'.debug_line'  			SHT_PROGBITS					0x0		0x32cb	0x7f	0x0	0x0	0x1	0x0
29	0x126			b'.debug_str'   			SHT_PROGBITS		MS			0x0		0x334a	0xf5	0x0	0x0	0x1	0x1
30	0x1			b'.symtab'      			SHT_SYMTAB						0x0		0x3440	0x5a0	0x1f	0x34	0x8	0x18
31	0x9			b'.strtab'      			SHT_STRTAB						0x0		0x39e0	0x1c3	0x0	0x0	0x1	0x0
32	0x11			b'.shstrtab'    			SHT_STRTAB						0x0		0x3ba3	0x131	0x0	0x0	0x1	0x0
```

La seule table supplémentaire est la section `.debug_str`. Quatres autres sections (`debug_aranges`, `debug_info`, `debug_abbrev` et `debug_line`) ont été ajoutées.

# Pourquoi des sections ET des segments ?

## TL;DR : 
- Les segments disent comment fabriquer l'image mémoire du fichier pour l'exécuter.
- Les sections disent ce que contient le fichier.
- La table des en-têtes de sections n'est pas nécessaire à l'exécution du programme.
- Par contre elle aide la retroconception !

# Et si on strip ?

On strip notre bibliothèque partagée :

```
$ cp dummylib.so dummylib.so.bak
$ strip dummylib.so
$ ls -ltr
(...)
-rwxr-xr-x 1 thomas thomas   16176 19 juil. 19:30 dummylib.so.bak
-rwxr-xr-x 1 thomas thomas   14256 19 juil. 19:30 dummylib.so
```

Sa taille a diminuée.

```
n°	offset_name	name							type					flags		vaddr		offset	size	link	info	align	entsize
0	0x0			b''             			SHT_NULL							0x0		0x0		0x0	0x0	0x0	0x0	0x0
1	0xb			b'.note.gnu.build-id'	SHT_NOTE				A			0x238		0x238		0x24	0x0	0x0	0x4	0x0
2	0x1e			b'.gnu.hash'    			unknown sh_type	A			0x260		0x260		0x30	0x3	0x0	0x8	0x0
3	0x28			b'.dynsym'      			SHT_DYNSYM			A			0x290		0x290		0xd8	0x4	0x1	0x8	0x18
4	0x30			b'.dynstr'      			SHT_STRTAB			A			0x368		0x368		0x90	0x0	0x0	0x1	0x0
5	0x38			b'.gnu.version' 			unknown sh_type	A			0x3f8		0x3f8		0x12	0x3	0x0	0x2	0x2
6	0x45			b'.gnu.version_r'			unknown sh_type	A			0x410		0x410		0x20	0x4	0x1	0x8	0x0
7	0x54			b'.rela.dyn'    			SHT_RELA				A			0x430		0x430		0xa8	0x3	0x0	0x8	0x18
8	0x5e			b'.rela.plt'    			SHT_RELA				AI			0x4d8		0x4d8		0x18	0x3	0x15	0x8	0x18
9	0x68			b'.init'        			SHT_PROGBITS		AX			0x1000	0x1000	0x17	0x0	0x0	0x4	0x0
10	0x63			b'.plt'         			SHT_PROGBITS		AX			0x1020	0x1020	0x20	0x0	0x0	0x10	0x10
11	0x6e			b'.plt.got'     			SHT_PROGBITS		AX			0x1040	0x1040	0x8	0x0	0x0	0x8	0x8
12	0x77			b'.text'        			SHT_PROGBITS		AX			0x1050	0x1050	0x19e	0x0	0x0	0x10	0x0
13	0x7d			b'.fini'        			SHT_PROGBITS		AX			0x11f0	0x11f0	0x9	0x0	0x0	0x4	0x0
14	0x83			b'.rodata'      			SHT_PROGBITS		A			0x2000	0x2000	0x82	0x0	0x0	0x8	0x0
15	0x8b			b'.eh_frame_hdr'			SHT_PROGBITS		A			0x2084	0x2084	0x34	0x0	0x0	0x4	0x0
16	0x99			b'.eh_frame'    			SHT_PROGBITS		A			0x20b8	0x20b8	0xbc	0x0	0x0	0x8	0x0
17	0xa3			b'.init_array'  			SHT_INIT_ARRAY		WA			0x3e10	0x2e10	0x8	0x0	0x0	0x8	0x8
18	0xaf			b'.fini_array'  			SHT_FINI_ARRAY		WA			0x3e18	0x2e18	0x8	0x0	0x0	0x8	0x8
19	0xbb			b'.dynamic'     			SHT_DYNAMIC			WA			0x3e20	0x2e20	0x1c0	0x4	0x0	0x8	0x10
20	0x72			b'.got'         			SHT_PROGBITS		WA			0x3fe0	0x2fe0	0x20	0x0	0x0	0x8	0x8
21	0xc4			b'.got.plt'     			SHT_PROGBITS		WA			0x4000	0x3000	0x20	0x0	0x0	0x8	0x8
22	0xcd			b'.data'        			SHT_PROGBITS		WA			0x4020	0x3020	0x8	0x0	0x0	0x8	0x0
23	0xd3			b'.bss'         			SHT_NOBITS			WA			0x4028	0x3028	0x8	0x0	0x0	0x1	0x0
24	0xd8			b'.comment'     			SHT_PROGBITS		MS			0x0		0x3028	0x27	0x0	0x0	0x1	0x1
25	0x1			b'.shstrtab'    			SHT_STRTAB						0x0		0x304f	0xe1	0x0	0x0	0x1	0x0
```

Les sections `.symtab` et `.strtab` ont disparues !

La section `.strtab` a le contenu ci-dessous :

```
$ readelf -p .strtab ./dummylib.so.bak
Vidange textuelle de la section « .strtab » :
  [     1]  crtstuff.c
  [     c]  deregister_tm_clones
  [    21]  __do_global_dtors_aux
  [    37]  completed.0
  [    43]  __do_global_dtors_aux_fini_array_entry
  [    6a]  frame_dummy
  [    76]  __frame_dummy_init_array_entry
  [    95]  dummylib.c
  [    a0]  __FUNCTION__.2
  [    af]  __FUNCTION__.1
  [    be]  __FUNCTION__.0
  [    cd]  __FRAME_END__
  [    db]  _fini
  [    e1]  __dso_handle
  [    ee]  _DYNAMIC
  [    f7]  __GNU_EH_FRAME_HDR
  [   10a]  __TMC_END__
  [   116]  _GLOBAL_OFFSET_TABLE_
  [   12c]  _init
  [   132]  _ITM_deregisterTMCloneTable
  [   14e]  function1
  [   158]  function3
  [   162]  printf@GLIBC_2.2.5
  [   175]  __gmon_start__
  [   184]  function2
  [   18e]  _ITM_registerTMCloneTable
  [   1a8]  __cxa_finalize@GLIBC_2.2.5
```

# Résumé succint du rôle de chaque section

En plus de la lecture des fichiers .h pertinents et de la documentation les concernants, la commande

`objdump -j <nom_section> ./dummylib_debug.so  -s` permet de dumper le contenu d'une section pour mieux en comprendre le rôle.

On peut aussi utiliser `readelf -x <nom_section> ./dummylib_debug.so`, ou `readelf -p <nom_section> ./dummylib_debug.so`.

- `.bss` : bss = "Block Started by Symbol". Cette section contient des données non initialisées.

- `.comment` : Contient des informations de contrôle de version, portant sur le compilateur par exemple :

```
$ readelf -x .comment ./dummylib*so*

Fichier: ./dummylib_debug.so

Vidange hexadécimale de la section « .comment » :
  0x00000000 4743433a 20284465 6269616e 2031302e GCC: (Debian 10.
  0x00000010 322e312d 36292031 302e322e 31203230 2.1-6) 10.2.1 20
  0x00000020 32313031 313000                     210110.

Fichier: ./dummylib.so

Vidange hexadécimale de la section « .comment » :
  0x00000000 4743433a 20284465 6269616e 2031302e GCC: (Debian 10.
  0x00000010 322e312d 36292031 302e322e 31203230 2.1-6) 10.2.1 20
  0x00000020 32313031 313000                     210110.

Fichier: ./dummylib.so.bak

Vidange hexadécimale de la section « .comment » :
  0x00000000 4743433a 20284465 6269616e 2031302e GCC: (Debian 10.
  0x00000010 322e312d 36292031 302e322e 31203230 2.1-6) 10.2.1 20
  0x00000020 32313031 313000                     210110.

$ readelf -x .comment ./toto

Vidange hexadécimale de la section « .comment » :
  0x00000000 4743433a 20284465 6269616e 2031302e GCC: (Debian 10.
  0x00000010 322e312d 36292031 302e322e 31203230 2.1-6) 10.2.1 20
  0x00000020 32313031 313000                     210110.
```

- `.data` : Contient les données initialisées. Faisons une petite expérience avec toto.c. Ce dernier contient une variable globale `m` initialisée :

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int m = 12;
unsigned char *secret = "crepeausucre";
```

Si l'on dumpe (on vidange !) `toto`, on observe la valeur de `m`, égale à `0x0c` :

```
$ readelf -x .data ./toto

Vidange hexadécimale de la section « .data » :
  0x00003438 00000000 00000000 40340000 00000000 ........@4......
  0x00003448 0c000000 00000000 04200000 00000000 ......... ......
```

Si l'on recompile après avoir assigné à `m` la valeur 666 (`0x29a`), le contenu de `.data` s'en trouve modifié :

```
$ readelf -x .data ./toto

Vidange hexadécimale de la section « .data » :
  0x00004040 00000000 00000000 48400000 00000000 ........H@......
  0x00004050 9a020000 00000000 04200000 00000000 ......... ......
```

- `.dynamic` :

```
$ readelf -x .dynamic dummylib.so

Vidange hexadécimale de la section « .dynamic » :
  0x00003e20 01000000 00000000 7a000000 00000000 ........z.......
  0x00003e30 0c000000 00000000 00100000 00000000 ................
  0x00003e40 0d000000 00000000 f0110000 00000000 ................
  0x00003e50 19000000 00000000 103e0000 00000000 .........>......
  0x00003e60 1b000000 00000000 08000000 00000000 ................
  0x00003e70 1a000000 00000000 183e0000 00000000 .........>......
  0x00003e80 1c000000 00000000 08000000 00000000 ................
  0x00003e90 f5feff6f 00000000 60020000 00000000 ...o....`.......
  0x00003ea0 05000000 00000000 68030000 00000000 ........h.......
  0x00003eb0 06000000 00000000 90020000 00000000 ................
  0x00003ec0 0a000000 00000000 90000000 00000000 ................
  0x00003ed0 0b000000 00000000 18000000 00000000 ................
  0x00003ee0 03000000 00000000 00400000 00000000 .........@......
  0x00003ef0 02000000 00000000 18000000 00000000 ................
  0x00003f00 14000000 00000000 07000000 00000000 ................
  0x00003f10 17000000 00000000 d8040000 00000000 ................
  0x00003f20 07000000 00000000 30040000 00000000 ........0.......
  0x00003f30 08000000 00000000 a8000000 00000000 ................
  0x00003f40 09000000 00000000 18000000 00000000 ................
  0x00003f50 feffff6f 00000000 10040000 00000000 ...o............
  0x00003f60 ffffff6f 00000000 01000000 00000000 ...o............
  0x00003f70 f0ffff6f 00000000 f8030000 00000000 ...o............
  0x00003f80 f9ffff6f 00000000 03000000 00000000 ...o............
  0x00003f90 00000000 00000000 00000000 00000000 ................
  0x00003fa0 00000000 00000000 00000000 00000000 ................
  0x00003fb0 00000000 00000000 00000000 00000000 ................
  0x00003fc0 00000000 00000000 00000000 00000000 ................
  0x00003fd0 00000000 00000000 00000000 00000000 ................
```

Parsons cette section. D'après ce que l'on a vu auparavant,
cette section est une table constituée d'entrées de 0x10 octets.

Dans sa grande bonté, le `man` de `elf` nous apprend que cette section un tableau de `Elf64_Dyn` :

```
typedef struct {
	Elf64_Sxword    d_tag; // tag spécifiant comment d_un doit être interprété
	union {
		Elf64_Xword d_val;  // valeur entière dont l'interprétation dépend du contexte
		Elf64_Addr  d_ptr;  // adresse virtuelle
	} d_un;
} Elf64_Dyn;
extern Elf64_Dyn _DYNAMIC[];
```

La section `.dynamic` de notre exemple contient les `Elf64_Dyn` ci-dessous :

```
0100000000000000 # d_tag = 0x01 = DT_NEEDED => d_ptr est l'offset dans .dynstr du nom d'une bibliothèque partagée iiiiiiiindisssssssssspensable.
7a00000000000000 # d_tag = DT_NEEDED => d_un = d_ptr = 0x7a

Comme de par hasard, une "vidange" (les traductions étant ce qu'elles sont) la section .dynstr nous informe qu'à l'offset 0x7a on y trouve la libc :

$ readelf -p .dynstr ./dummylib.so

Vidange textuelle de la section « .dynstr » :
  [     1]  __gmon_start__
  [    10]  _ITM_deregisterTMCloneTable
  [    2c]  _ITM_registerTMCloneTable
  [    46]  __cxa_finalize
  [    55]  function1
  [    5f]  printf
  [    66]  function2
  [    70]  function3
  [    7a]  libc.so.6
  [    84]  GLIBC_2.2.5

0c00000000000000 # d_tag = 0x0c = DT_INIT => d_ptr est l'adresse d'une fonction d'initialisation. En l'occurrence, c'est l'adresse dans le binaire de la section .init.
0010000000000000 # d_tag = DT_INIT => d_un = d_ptr = 0x1000

0d00000000000000 # d_tag = 0x0d = DT_FINI => même bail mais avec la section .fini. 
f011000000000000 # d_tag = DT_FINI => d_un = d_ptr = 0x11f0 

1900000000000000 # d_tag = 0x19 = DT_INIT_ARRAY => idem mais avec .init_array.
103e000000000000 # d_tag = DT_INIT_ARRAY => d_un = d_ptr = 0x3e10

1b00000000000000 # d_tag = 0x1b = DT_INIT_ARRAYSZ => taille du DT_INIT_ARRAY
0800000000000000 # d_tag = DT_INIT_ARRAYSZ => d_un = d_val = 0x08

1a00000000000000 # d_tag = 0x1a = DT_FINI_ARRAY => même limonade queDT_INIT_ARRAY
183e000000000000 # d_tag = DT_FINI_ARRAY => d_un = d_ptr = 0x3e18

1c00000000000000 # d_tag = 0x1c = DT_FINI_ARRAYSZ => taille du DT_FINI_ARRAY
0800000000000000 # d_tag = DT_FINI_ARRAYSZ => d_un = d_val = 0x08

f5feff6f00000000 # d_tag = 0x6ffffef5 => d_ptr est l'adreses de .gnu.hash
6002000000000000 # d_un = d_ptr = 0x260

0500000000000000 # d_tag = 0x05 = DT_STRTAB => d_ptr est l'adreses de .dynstr
6803000000000000 # d_tag = DT_STRTAB => d_un = d_ptr = 0x0368

0600000000000000 # d_tag = 0x06 = DT_SYMTAB => d_ptr est l'adresse de .dynsym
9002000000000000 # d_tag = DT_SYMTAB => d_un = d_ptr = 0x0290

0a00000000000000 # d_tag = 0x0a = DT_STRSZ => d_val est la taille de .dynstr
9000000000000000 # d_tag = DT_STRSZ => d_un = d_val = 0x90

0b00000000000000 # d_tag = 0x0b = DT_SYMENT => d_val est la taille d'une entrée de.dynsym
1800000000000000 # d_tag = DT_SYMENT => d_un = d_val = 0x18

0300000000000000 # d_tag = 0x03 = DT_PLTGOT => d_ptr est l'adresse de .got.plt
0040000000000000 # d_tag = DT_PLTGOT => d_un = d_ptr = 0x4000

0200000000000000 # d_tag = 0x02 = DT_PLTRELSZ => d_val est la taille des entrées de .rela.plt
1800000000000000 # d_tag = DT_PLTRELSZ => d_un = d_val = 0x18

1400000000000000 # d_tag = 0x14 = DT_PLTREL => d_val indique le type de relocation.
0700000000000000 # d_tag = DT_PLTREL => d_un = d_val = 0x07

1700000000000000 # d_tag = 0x17 = DT_JMPREL => d_ptr indique l'adresse de .rela.plt 
d804000000000000 # d_tag = DT_JMPREL => d_un = d_ptr = 0x04d8

0700000000000000 # d_tag = 0x07 = DT_RELA => d_ptr est l'adresse de .rela.dyn
3004000000000000 # d_tag = DT_RELA => d_un = d_ptr = 0x0430

0800000000000000 # d_tag = 0x08 = DT_RELASZ =>  d_val est la taille de .rela.dyn
a800000000000000 # d_tag = DT_RELASZ => d_un = d_val = 0xa8

0900000000000000 # d_tag = 0x09 = DT_RELAENT => d_val est la taille des entrées de .rela.dyn
1800000000000000 # d_tag = DT_RELAENT => d_un = d_val = 0x18

feffff6f00000000 # d_tag = 0x6ffffffe = DT_VERNEED => d_ptr est l'adresse de la section .gnu.version_r
1004000000000000 # d_tag = DT_VERNEED => d_un = d_ptr = 0x0410

ffffff6f00000000 # d_tag = 0x6fffffff = DT_VERNEEDNUM => d_val est le nombre d'entrée de .gnu.version_r
0100000000000000 # d_tag = DT_VERNEEDNUM => d_un = d_val = 0x01

f0ffff6f00000000 # d_tag = 0x6ffffff0 = DT_VERSYM => d_ptr est l'adresse de la section .gnu.version
f803000000000000 # d_tag = DT_VERSYM => d_un = d_ptr = 0x03f8

f9ffff6f00000000 # d_tag = 0x6ffffff9 = DT_RELACOUNT => d_val semble être un compteur impliqué dans le processus de relocation.
0300000000000000 # d_tag = DT_RELACOUNT => d_un = d_val = 0x03

0000000000000000 # d_tag = 0x00 = DT_NULL
0000000000000000

0000000000000000 # d_tag = 0x00 = DT_NULL
0000000000000000

0000000000000000 # d_tag = 0x00 = DT_NULL
0000000000000000

0000000000000000 # d_tag = 0x00 = DT_NULL
0000000000000000

0000000000000000 # d_tag = 0x00 = DT_NULL
0000000000000000
```

- `.dynsym` : D'après https://llvm.org/doxygen/BinaryFormat_2ELF_8h_source.html, le contenu de cette section :

```
$ readelf -x .dynsym ./dummylib.so.bak 
Vidange hexadécimale de la section « .dynsym » :
  0x00000290 00000000 00000000 00000000 00000000 ................
  0x000002a0 00000000 00000000 10000000 20000000 ............ ...
  0x000002b0 00000000 00000000 00000000 00000000 ................
  0x000002c0 5f000000 12000000 00000000 00000000 _...............
  0x000002d0 00000000 00000000 01000000 20000000 ............ ...
  0x000002e0 00000000 00000000 00000000 00000000 ................
  0x000002f0 2c000000 20000000 00000000 00000000 ,... ...........
  0x00000300 00000000 00000000 46000000 22000000 ........F..."...
  0x00000310 00000000 00000000 00000000 00000000 ................
  0x00000320 70000000 12000c00 a3110000 00000000 p...............
  0x00000330 4b000000 00000000 55000000 12000c00 K.......U.......
  0x00000340 05110000 00000000 46000000 00000000 ........F.......
  0x00000350 66000000 12000c00 4b110000 00000000 f.......K.......
  0x00000360 58000000 00000000                   X.......
```

Est contitué d'entrées de 0x18 octets :

```
struct Elf64_Sym {
  Elf64_Word st_name;     // Symbol name (index into string table)
  unsigned char st_info;  // Symbol's type and binding attributes
  unsigned char st_other; // Must be zero; reserved
  Elf64_Half st_shndx;    // Which section (header tbl index) it's defined in
  Elf64_Addr st_value;    // Value or address associated with the symbol
  Elf64_Xword st_size;    // Size of the symbol
}
```

- Le premier champ de 4 octets est l'index du nom du symbole dans la table `.dynstr`.
- Le deuxième champs, de 1 octet, indique le binding et le type du symbole.
- Le troisième champ, de 1 octet, vaut toujours zéro.
- Le quatrième champ, de 2 octets, indique dans quelle section est défini le symbole.
- Le cinquième champ, de 8 octets, est l'adresse associée au symbole dans le binaire.
- Le dernier champ, de 8 octets, est la taille du symbole dans le binaire.

## .dynsym, `st_info` : 

Le contenu de `st_info` se parse en `(binding << 4) + (type & 0x0F)`.

Les valeurs de binding possibles sont :

```
STB_LOCAL  = 0 // symbole local non visible hors de l'obj contenant la définition
STB_GLOBAL = 1 // symbole global
STB_WEAK   = 2 // symbole faible : global mais avec "faible" priorité
STB_GNU_UNIQUE = 10
STB_LOOS = 10
STB_HIOS = 12
STB_LOPROC = 13
STB_HIPROC = 15
```

Les valeurs de type possibles sont :

```
STT_NOTYPE = 0	// type non spécifié
STT_OBJECT = 1	// donnée (variable, tableau, etc)
STT_FUNC   = 2 // le symbole est exécutable
STT_SECTION = 3 // le symbole fait référence à une section
STT_FILE   = 4 // le symbole fait référence à un fichier
STT_COMMON = 5
STT_TLS    = 6
STT_GNU_IFUNC = 10
STT_LOOS = 10
STT_HIOS = 12
STT_LOPROC = 13
STT_HIPROC = 15
STT_AMDGPU_HSA_KERNEL = 10
```

Et aussi, la section `.dynstr` contient ceci :

```
$ readelf -p .dynstr ./dummylib.so.bak 

Vidange textuelle de la section « .dynstr » :
  [     1]  __gmon_start__
  [    10]  _ITM_deregisterTMCloneTable
  [    2c]  _ITM_registerTMCloneTable
  [    46]  __cxa_finalize
  [    55]  function1
  [    5f]  printf
  [    66]  function2
  [    70]  function3
  [    7a]  libc.so.6
  [    84]  GLIBC_2.2.5
```

## dis-section de la section `.dynsym`

Compte tenu de tout ceci, la section `dynsym` se parse en ceci :

```
00000000				# st_name = 0 -> entrée vide dans .dynstr
20						# st_info = 00h = 0 = 0 + 0 -> binding = STB_LOCAL, type = STT_NOTYPE
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

10000000 			# st_name = 0x10 -> entrée _ITM_deregisterTMCloneTable dans .dynstr
20						# st_info = 20h = 32 = 32 + 0 -> binding = STB_WEAK, type = STT_NOTYPE
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

5f000000				# st_name = 0x5f -> entrée printf dans .dynstr
12						# st_info = 12h = 18 = 16 + 2 -> binding = STB_GLOBAL, type = STT_FUNC
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

01000000 			# st_name = 0x01 -> entrée __gmon_start__ dans .dynstr
20						# st_info = 20h = 32 = 32 + 0 -> binding = STB_WEAK, type = STT_NOTYPE
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

2c000000 			# st_name = 0x2c -> entrée _ITM_registerTMCloneTable dans .dynstr
20						# st_info = 20h = 32 = 32 + 0 -> binding = STB_WEAK, type = STT_NOTYPE
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

46000000 			# st_name = 0x46 -> entrée __cxa_finalize dans .dynstr
22						# st_info = 22h = 34 = 32 + 2 -> binding = STB_WEAK, type = STT_FUNC
00						# st_other
0000 					# st_shndx -> défintion dans la section n°0, càd nulle part
00000000 00000000
00000000 00000000

70000000 			# st_name = 0x70 -> entrée function3 dans .dynstr
12						# st_info = 12h = 18 = 16 + 2 -> binding = STB_GLOBAL, type = STT_FUNC
00						# st_other
0c00 					# st_shndx -> définition dans la section d'index 0c, ie dans la section .text
a3110000 00000000	# st_value : function3
4b000000 00000000 # st_size : taille du code assembleur

55000000 			# st_name = 0x55 -> entrée function1 dans .dynstr
12						# st_info = 12h = 18 = 16 + 2 -> binding = STB_GLOBAL, type = STT_FUNC
00						# st_other
0c00 					# st_shndx -> définition dans la section d'index 0c, ie dans la section .text
05110000 00000000	# st_value : adresse de function1
46000000 00000000 # st_size :taille du code assembleur

66000000 			# st_name = 0x66 -> entrée function2 dans .dynstr
12						# st_info = 12h = 18 = 16 + 2 -> binding =  STB_GLOBAL, type = STT_FUNC
00						# st_other
0c00 					# st_shndx -> définition dans la section d'index 0c, ie dans la section .text
4b110000 00000000	# st_value : adresse de function2()
58000000 00000000 # st_size : taille du code assembleur
```

Les valeurs de `st_value` et `st_size` peuvent être corroborées par `objdump -d -j .text <fichier>`

Maintenant qu'on a compris tout ça, les prochaines fois on pourra se contenter de lancer :

```
$ objdump -T ./dummylib.so 

./dummylib.so:     format de fichier elf64-x86-64

DYNAMIC SYMBOL TABLE:
0000000000000000  w   D  *UND*	0000000000000000              _ITM_deregisterTMCloneTable
0000000000000000      DF *UND*	0000000000000000  GLIBC_2.2.5 printf
0000000000000000  w   D  *UND*	0000000000000000              __gmon_start__
0000000000000000  w   D  *UND*	0000000000000000              _ITM_registerTMCloneTable
0000000000000000  w   DF *UND*	0000000000000000  GLIBC_2.2.5 __cxa_finalize
00000000000011a3 g    DF .text	000000000000004b  Base        function3
0000000000001105 g    DF .text	0000000000000046  Base        function1
000000000000114b g    DF .text	0000000000000058  Base        function2
```

Notons que cette commande donne le même résultat sur le .so compilé en mode débug, et sur le .so non strippé !

- `.dynstr` : compte tenu de tout ce qui précéde, cette section contient les noms des symboles présents dans la section `.dynsym`.

- `.eh_frame` : cf `.eh_frame_hdr`. Si vous venez de `.eh_frame_hdr`, allez donc voir `.fini`.

- `.eh_frame_hdr` : cf `.eh_frame`.

- `.fini` : Rôle similaire à la section `.init`, voir plus bas.

- `.fini_array` : Rôle similaire à la section `.init_array`, voir plus bas.

- `.gnu.hash` : Contient un haché des symboles.

- `.gnu.version` : Cette section est utilisé dans le mécanisme de versioning des symboles, permettant de donner un numéro de version à des symboles. Plus d'informations sur https://refspecs.linuxbase.org/LSB_5.0.0/LSB-Core-generic/LSB-Core-generic/symversion.html.

- `.gnu.version_r` : Idem.

- `.got` : Section utilisée pour la résolution dynamique des symboles. Voir plus bas.

- `.got.plt` : Idem.

- `.init` : Contient du code qui sera à l'initialisation du programme :


```
$ readelf -x .init  ./toto 

Vidange hexadécimale de la section « .init » :
  0x00001000 4883ec08 488b05dd 2f000048 85c07402 H...H.../..H..t.
  0x00001010 ffd04883 c408c3                     ..H....

$ objdump -j .init -d ./toto

./toto:     format de fichier elf64-x86-64


Déassemblage de la section .init :

0000000000001000 <_init>:
    1000:	48 83 ec 08          	sub    $0x8,%rsp
    1004:	48 8b 05 dd 2f 00 00 	mov    0x2fdd(%rip),%rax        # 3fe8 <__gmon_start__>
    100b:	48 85 c0             	test   %rax,%rax
    100e:	74 02                	je     1012 <_init+0x12>
    1010:	ff d0                	callq  *%rax
    1012:	48 83 c4 08          	add    $0x8,%rsp
    1016:	c3                   	retq
```

- `.init_array` : Contient des pointeurs vers des fonctions exécutées à l'initialisation du programme :

```
$ readelf -x .init_array  ./toto 

Vidange hexadécimale de la section « .init_array » :
  0x00003de8 70110000 00000000                   p.......
  

$ objdump -j .text -d ./toto

./toto:     format de fichier elf64-x86-64


Déassemblage de la section .text :
(...)  
0000000000001170 <frame_dummy>:
    1170:	e9 7b ff ff ff       	jmpq   10f0 <register_tm_clones>
```

- `note.gnu.build-id` : Contient un identifiant unique de build.

- `.plt` : Section utilisée pour la résolution dynamique des symboles. Voir plus bas.

- `.plt.got` : Section utilisée pour la résolution dynamique des symboles. Voir plus bas.

- `.rela.dyn` : C'est une table d'entrées de 0x18 octets.

Cette table est utilisée par le processus de relocalisation. Ce processus consiste à réecrire des trucs au bon endroit. Lire les références pour plus de détail.

La section `.rela.dyn` contient des entrées de type `Elf64_Rela` :

```
typedef struct {
        Elf64_Addr      r_offset;	# Adresse sur 8 octets spécifiant l'adresse où s'applique la relocalisation.
        Elf64_Xword     r_info;		# Cette valeur contient l'index du symbole, et le type de relocalisation à effectuer.
        Elf64_Sxword    r_addend;   # Valeur utilisée pour calculer la valeur finale de relocalisation.
} Elf64_Rela;
```

L'interprétation du champ `r_info` se base sur ces 3 macros :

```
#define ELF64_R_SYM(info)             ((info)>>32)
#define ELF64_R_TYPE(info)            ((Elf64_Word)(info))
#define ELF64_R_INFO(sym, type)       (((Elf64_Xword)(sym)<<32)+ (Elf64_Xword)(type))
```

TL;DR : Les 4 octets de poids fort de `r_info` indiquent l'index du symbole et les 4 octets de poids faible indiquent le type de relocalisation.

Pour un objet relogeable (un `.o` par exemple), `r_offset` est un offset de section.
Pour un shared object ou un exécutable, `r_offset` est une adresse virtuelle.

La section `.rela.dyn` de `dummylib.so` contient ceci :

```
103e000000000000 # r_offset = 0x3e10 : Adresse de la section .init_array
0800000000000000 # r_info = 0x08 : R_X86_64_RELATIVE
0011000000000000 # r_addend = 0x1100 => adresse finale = r_offset + r_addend

183e000000000000 # r_offset = 0x3e18 : Adresse de la section .fini_array
0800000000000000 # r_info = 0x08 : R_X86_64_RELATIVE
c010000000000000 # r_addend = 0x10c0 => adresse finale = r_offset + r_addend

2040000000000000 # r_offset = 0x4020 : Adresse de la section .data
0800000000000000 # r_info = 0x08 : R_X86_64_RELATIVE
2040000000000000 # r_addend = 0x0420 => adresse finale = r_offset + r_addend

e03f000000000000 # r_offset = 0x3fe0 : Adresse de la section .got : 1ère entrée de .got
0600000001000000 # r_info = 0x0000000100000006 = 0x00000001 << 32 + 00000006 ; 0x06 =  R_X86_64_GLOB_DAT : On écrit l'adresse d'un symbole dans la .got. Ce symbole est le 1er de la section .dynsym.
0000000000000000 # r_addend = 0x0000 => adresse finale = r_offset

e83f000000000000 # r_offset = 0x3fe8 : Offset +8 dans la section .got : 3ème entrée de .got
0600000003000000 # r_info = 0x0000000300000006 = 0x00000003 << 32 + 00000006 ; 0x06 =  R_X86_64_GLOB_DAT : On écrit l'adresse d'un symbole dans la .got. Ce symbole est le 3ème de la section .dynsym.
0000000000000000 # r_addend = 0x0000 => adresse finale = r_offset

f03f000000000000 # r_offset = 0x3ff0 : Offset +0x10 dans la section .got : 4ème entrée de .got
0600000004000000 # r_info = 0x0000000400000006 = 0x00000004 << 32 + 00000006 ; 0x06 =  R_X86_64_GLOB_DAT : On écrit l'adresse d'un symbole dans la .got. Ce symbole est le 4ème de la section .dynsym.
0000000000000000 # r_addend = 0x0000 => adresse finale = r_offset

f83f000000000000 # r_offset = 0x3ff8 : Offset +0x18 dans la section .got : 5ème entrée de .got
0600000005000000 # r_info = 0x0000000500000006 = 0x00000005 << 32 + 00000006 ; 0x06 =  R_X86_64_GLOB_DAT : On écrit l'adresse d'un symbole dans la .got. Ce symbole est le 5ème de la section .dynsym.
0000000000000000 # r_addend = 0x0000 => adresse finale = r_offset
```

Pour les gens qui n'aiment pas parser les sections à la mains, les relocations peuvent être listées avec `readelf -r` :

```
$ readelf -r ./dummylib.so -W

Section de réadressage '.rela.dyn' à l'adresse de décalage 0x430 contient 7 entrées:
    Décalage           Info             Type               Valeurs symbols Noms symboles + Addenda
0000000000003e10  0000000000000008 R_X86_64_RELATIVE                         1100
0000000000003e18  0000000000000008 R_X86_64_RELATIVE                         10c0
0000000000004020  0000000000000008 R_X86_64_RELATIVE                         4020
0000000000003fe0  0000000100000006 R_X86_64_GLOB_DAT      0000000000000000 _ITM_deregisterTMCloneTable + 0
0000000000003fe8  0000000300000006 R_X86_64_GLOB_DAT      0000000000000000 __gmon_start__ + 0
0000000000003ff0  0000000400000006 R_X86_64_GLOB_DAT      0000000000000000 _ITM_registerTMCloneTable + 0
0000000000003ff8  0000000500000006 R_X86_64_GLOB_DAT      0000000000000000 __cxa_finalize@GLIBC_2.2.5 + 0
```

Section de réadressage '.rela.plt' à l'adresse de décalage 0x4d8 contient 1 entrée:
    Décalage           Info             Type               Valeurs symbols Noms symboles + Addenda
0000000000004018  0000000200000007 R_X86_64_JUMP_SLOT     0000000000000000 printf@GLIBC_2.2.5 + 0

- `.rela.plt` :

C'est comme la section précédente !

```
1840000000000000 # r_offset = 0x4018
0700000002000000 # r_info = 0x00000007 << 32 + 00000002 ; 0x02 = R_X86_64_PC32 : 2ème symbole de la section .dynsym.
0000000000000000 # r_addend = 0
```

- `.rodata` : Contient des données en lecture-seule :

```
$ readelf -p .rodata ./dummylib_debug.so 

Vidange textuelle de la section « .rodata » :
  [     0]  %s : function1(%d, %d) = %d\n
  [    1d]  %s : function2(%d, %d) = %d\n
  [    3a]  %s : function3(%d, %d) = %d\n
  [    58]  function1
  [    68]  function2
  [    78]  function3

$ readelf -p .rodata ./toto

Vidange textuelle de la section « .rodata » :
  [     4]  crepeausucre
  [    11]  usage !
  [    19]  %X:
  [    1d]  %X\n
```

- `.strtab` : Cette section contient les noms des symboles présents dans `.symtab`.

- `.symtab` : À l'instar de `.dynsym`, cette section contient des symboles. Cependant, à la différence de sa consoeur,

cette section
1/ n'est pas mappée en mémoire à l'exécution (cf plus bas paragraphe Correspondance sections / segments)
2/ est supprimée si l'on strip le programme (cf ci-dessus).

- `.text` : C'est le code exécutable du fichier. On peut desassembler cette section avec `objdump -j .text -d ./toto` :

```
$ objdump -d -j .text ./toto

./toto:     format de fichier elf64-x86-64


Déassemblage de la section .text :

0000000000001090 <_start>:
    1090:	31 ed                	xor    %ebp,%ebp
    1092:	49 89 d1             	mov    %rdx,%r9
    1095:	5e                   	pop    %rsi
    1096:	48 89 e2             	mov    %rsp,%rdx
    1099:	48 83 e4 f0          	and    $0xfffffffffffffff0,%rsp
    109d:	50                   	push   %rax
    109e:	54                   	push   %rsp
    109f:	4c 8d 05 fa 02 00 00 	lea    0x2fa(%rip),%r8        # 13a0 <__libc_csu_fini>
    10a6:	48 8d 0d 93 02 00 00 	lea    0x293(%rip),%rcx        # 1340 <__libc_csu_init>
    10ad:	48 8d 3d df 01 00 00 	lea    0x1df(%rip),%rdi        # 1293 <main>
    10b4:	ff 15 26 2f 00 00    	callq  *0x2f26(%rip)        # 3fe0 <__libc_start_main@GLIBC_2.2.5>
    10ba:	f4                   	hlt    
    10bb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
(...)
```

- `.shstrtab` : Cette section contient les noms des autres sections !

```
$ readelf -p .shstrtab ./toto

Vidange textuelle de la section « .shstrtab » :
  [     1]  .symtab
  [     9]  .strtab
  [    11]  .shstrtab
  [    1b]  .interp
  [    23]  .note.gnu.build-id
  [    36]  .note.ABI-tag
  [    44]  .gnu.hash
  [    4e]  .dynsym
  [    56]  .dynstr
  [    5e]  .gnu.version
  [    6b]  .gnu.version_r
  [    7a]  .rela.dyn
  [    84]  .rela.plt
  [    8e]  .init
  [    94]  .plt.got
  [    9d]  .text
  [    a3]  .fini
  [    a9]  .rodata
  [    b1]  .eh_frame_hdr
  [    bf]  .eh_frame
  [    c9]  .init_array
  [    d5]  .fini_array
  [    e1]  .dynamic
  [    ea]  .got.plt
  [    f3]  .data
  [    f9]  .bss
  [    fe]  .comment
```

# Correspondance sections / segments

En plus de lister les segments, la commande `readelf --segments ./dummylib.so -W` donne la liste des sections incluses dans chacun d'entre eux :

```
(...)
 Correspondance section/segment :
  Sections de segment...
   00     .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt 
   01     .init .plt .plt.got .text .fini 
   02     .rodata .eh_frame_hdr .eh_frame 
   03     .init_array .fini_array .dynamic .got .got.plt .data .bss 
   04     .dynamic 
   05     .note.gnu.build-id 
   06     .eh_frame_hdr 
   07     
   08     .init_array .fini_array .dynamic .got
```

# `.dynamic` vs `.dynsym` vs `.symtab`

- Les sections `.symtab` et `.dynsym` sont toutes deux des tables d'entrées (des symboles) de 0x18 octets. Chaque entrée contient les informations suivantes :
	- offset du symbole dans le fichier
	- taille du symboledans le fichier
	- index de la section où le symbole apparaît
	- index du nom du symbole dans table appropriée, `.dynstr` pour `.dynsym` et `.strtab` pour `.symtab`.

- Cependant, à la différence de la section `.symtab`, la section `.dynsym` fait partie d'un segment de type `PT_LOAD` et est donc bien présente dans l'image mémoire du binaire.

- Par ailleurs, la section `.symtab` est supprimée du fichier si ce dernier est strippée. Elle n'est donc pas indispensable à l'exécution.

La section `.dynsym` peut être listée avec la commande `objdump -T` ou `objdump --dynamic-syms`, tandis que la section `.symtab` peut être listée avec `objdump -t`, ou `objdump --syms`.

- La section `.dynamic` est de nature différente de ces deux autres sections puisqu'elle est constituée d'entrées de 0x10 octets.
Cette section fait l'objet d'un segment dédié, le segment `PT_DYNAMIC`. Chacune de ces entrées spécifie l'emplacement et la taille d'une section du binaire.

# Zeroïzer les en-têtes de sections et voir ce qu'il advient

S'il est assez surprenant de prime abord que les en-têtes de sections ne soient pas indispensable au bon fonctionnement du binaire,
les supprimer peut aider à s'en convaincre :

```
cp /usr/bin/cat ./
$ readelf -h ./cat 
En-tête ELF:
  Magique:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Classe:                            ELF64
  Données:                          complément à 2, système à octets de poids faible d'abord (little endian)
  Version:                           1 (actuelle)
  OS/ABI:                            UNIX - System V
  Version ABI:                       0
  Type:                              DYN (fichier objet partagé)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Adresse du point d'entrée:         0x2ee0
  Début des en-têtes de programme :  64 (octets dans le fichier)
  Début des en-têtes de section :    42016 (octets dans le fichier)
  Fanions:                           0x0
  Taille de cet en-tête:             64 (octets)
  Taille de l'en-tête du programme:  56 (octets)
  Nombre d'en-tête du programme:     11
  Taille des en-têtes de section:    64 (octets)
  Nombre d'en-têtes de section:      30
  Table d'index des chaînes d'en-tête de section: 29
```

- 30 sections, donc 30 en-têtes de sections de 64 octets chacunes
- 1ère en-tête de section à l'adresse 42016, ie 0xA420.

On peut donc écraser les en-têtes de section avec dd :

```
dd if=/dev/zero of=./cat bs=1 count=1920 seek=42016
```

Le programme s'exécute normalement :

```
$ ./cat /etc/hosts
127.0.0.1	localhost
127.0.1.1	ankou

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```

# Mais que fait le loader ??

La variable LD_DEBUG peut apporter des éléments de réponse !

```
$ LD_DEBUG=help ls
Valid options for the LD_DEBUG environment variable are:

  libs        display library search paths
  reloc       display relocation processing
  files       display progress for input file
  symbols     display symbol table processing
  bindings    display information about symbol binding
  versions    display version dependencies
  scopes      display scope information
  all         all previous options combined
  statistics  display relocation statistics
  unused      determined unused DSOs
  help        display this help message and exit

To direct the debugging output into a file instead of standard output
a filename can be specified using the LD_DEBUG_OUTPUT environment variable.
```

On peut par entre autre chose regarder le processus de relocalisation :

```
$ LD_DEBUG=reloc ls
    372726:	
    372726:	relocation processing: /lib/x86_64-linux-gnu/libc.so.6 (lazy)
    372726:	
    372726:	relocation processing: /lib/x86_64-linux-gnu/libpthread.so.0 (lazy)
    372726:
(...)
```
