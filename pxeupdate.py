#!/usr/bin/env python3
#Author: slango20
#Description: PXE Netboot Repository tree updater
#Takes options as arrays set in the file
#TODO: set up arguments
#DONE: Config files for the script
#TODO: Add support for non-debian based repository trees (can arch netboot?) Use format string-like thing to determine order from config
#TODO: find a better way to download files that will skip if no changes (similar to rsync -u)
#TODO low: add per-file progress bar without bloated wget UI
#TODO: Make Modular (add classes for common distros to eliminate the looped distro-specific handling)
#TODO low: threading
#TODO: make core more generic
#DONE: add configuration generator

import json
import os
import sys

#added to special download strings to suppress wget output
suppress = " -N >/dev/null 2>&1" #add -N to all wget so it will be smart about re-fetching remote objects
if not os.path.exists("pxelinux.cfg"):
    os.makedirs("pxelinux.cfg")
try:
    with open('config.json', 'r') as conf:
        config = json.load(conf)
except json.decoder.JSONDecodeError as e:
    print("Malformed config file.")
    print(e)
    exit(1)
except FileNotFoundError:
    #Set sane defaults if config not found/config invalid (if not found will prompt to create with defaults)
    #amd64 and i386 are the most common
    architectures = ["amd64", "i386"]
    #Distribution of linux goes here, currently can only handle debian-based
    dists = ["debian"]
    #Distribution major releases
    rels = ["jessie", "sid"]
    #Files to get from the repository, must be populated
    targets = ["linux", "initrd.gz"]
    #Special targets, [0] is the name for the config generator, [1] is the URL the file can be found at, and [2] is the path for both the config generator and wget. [3] is fancy name
    special = [["grub_efi_amd64", "http://archive.ubuntu.com/ubuntu/dists/trusty/main/uefi/grub2-amd64/current/grubnetx64.efi.signed", "special/grub/amd64/grubnetx64.efi.signed", "amd64 GRUB EFI Netboot"]]

    print("Config file not found, should I create one with defaults?")
    if (query_yes_no("") == true ):
        config = {'distributions': {'ubuntu': {'targets': ['initrd.gz', 'linux'], 'architectures': ['amd64', 'i386'], 'append': '', 'archive': 'http://archive.ubuntu.com/', 'releases': ['trusty']}, 'debian': {'targets': ['initrd.gz', 'linux'], 'architectures': ['amd64', 'i386'], 'append': '', 'archive': 'ftp://ftp.us.debian.org/', 'releases': ['jessie', 'sid']}}, 'special': {'grub': {'targets': ['ubuntu/dists/trusty/main/uefi/grub2-amd64/current/grubnetx64.efi.signed'], 'architectures': ['amd64'], 'readable': 'Grub EFI Netloader', 'archive': 'http://archive.ubuntu.com/', 'lable': 'grub_efi_amd64', 'paths': ['special/grub/amd64/grubnetx64.efi.signed'], 'append': ''}}}
 #TODO low: make fancier
        with open('config.json', 'w') as conf:
            json.dump(config, conf, indent=4)
#print(config) #debug bits
#exit(0)
dists = config['distributions']
for dist in dists:
    rels = config['distributions'][dist]['releases']
    for rel in rels:
        architectures = config['distributions'][dist]['architectures']
        for arch in architectures:
            targets = config['distributions'][dist]['targets']
            for target in targets:
                outdir = dist+"/"+rel+"/"+arch+"/"
                installer="installer-"+arch #idiot, this is default
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                outfile = outdir+target
                print("Downloading "+target+" to "+outfile)
                archive= config['distributions'][dist]['archive']
                os.system("wget "+archive+dist+"/dists/" + rel + "/main/"+installer+"/current/images/netboot/"+dist+"-installer/"+arch+"/"+target+" -O "+outfile+suppress)
for spec in config['special']:
    os.system("wget "+config['special'][spec]['archive'][0]+config['special'][spec]['targets'][0]+" -O "+config['special'][spec]['paths'][0]+suppress) #Account for array
print("Generating Configuration File...")
conffile = open("pxelinux.cfg/default", "w")
conffile.write("default menu.c32\nmenu title PXE Boot System\ntimeout 32\n\n")
dists = config['distributions']
for dist in dists:
    rels = config['distributions'][dist]['releases']
    for rel in rels:
        architectures = config['distributions'][dist]['architectures']
        for arch in architectures:
            print("Adding "+dist+"_"+rel+"_"+arch+"...")
            conffile.write("lable "+dist+"_"+rel+"_"+arch+"\nmenu label "+dist+" "+rel+" "+arch+"\nkernel "+dist+"/"+rel+"/"+arch+"/linux\n")
            conffile.write("append initrd="+dist+"/"+rel+"/"+arch+"/initrd.img "+config['distributions'][dist]['append']+"\n\n")
for spec in config['special']:
    print(config['special'][spec]['lable'])
    conffile.write("lable "+config['special'][spec]['lable']+"\nmenu lable "+config['special'][spec]['readable']+"\nkernel "+config['special'][spec]['paths'][0]+"\nappend "+config['special'][spec]['append']) 
conffile.close() #technically uneeded unless this is being called directly into another python script
# Example generated entry:
# lable debian_jessie_amd64
# menu lable debian jessie amd64
# kernel debian/jessie/amd64/linux
# append initrd=debian/jessie/amd64/initrd.img


def query_yes_no(question, default="yes"):
#    """Ask a yes/no question via raw_input() and return their answer.
#
#    "question" is a string that is presented to the user.
#    "default" is the presumed answer if the user just hits <Enter>.
#        It must be "yes" (the default), "no" or None (meaning
#        an answer is required of the user).
#
#    The "answer" return value is True for "yes" or False for "no".
#    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
