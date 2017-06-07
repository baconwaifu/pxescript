#!/usr/bin/env python3
#Author: リン
#Description: PXE Netboot Repository tree updater
#License: DPMWTFYWT (Do Pretty Much Whatever The Fuck You Want To), details in LICENSE file
#Takes options as arrays set in the file
#distributions{} contains several instances of objects containing values such as the distribution, selected architectures, and selected releases for an APT repository
#special{} allows you to target absolute file paths for downloads, but is much the same as distribuitions{}
#append{} is to allow you to append arbitrary text to the end of the boot config (TODO: add a "head": and a "tail": element to allow replacing the boilerplate bootfile header [if head exists, don't write the header])
#TODO: better handling of problems with wget (primarily 404s due to people not respecting the true debian layout)
#TODO: set up arguments
#TODO: Add better support for non-debian based repository trees. 
#TODO: Use format string-like thing to determine order from config
#TODO: find a better way to download files that will skip if no changes (similar to rsync)
#TODO low: add per-file progress bar without bloated wget UI
#TODO low: multithreaded downloading (only across multiple mirrors, no more than one connection per mirror)

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
    #set sane defaults if config not found, prompt to create config with them.
    print("Config file not found, should I create one with defaults?")
    if (query_yes_no("") == true ):
        config = {'distributions': {'ubuntu': {'targets': ['initrd.gz', 'linux'], 'architectures': ['amd64', 'i386'], 'append': '', 'archive': 'http://archive.ubuntu.com/', 'releases': ['trusty','xenial']}, 'debian': {'targets': ['initrd.gz', 'linux'], 'architectures': ['amd64', 'i386'], 'append': '', 'archive': 'ftp://ftp.us.debian.org/', 'releases': ['jessie', 'sid']}}, 'special': {'grub': {'targets': ['ubuntu/dists/trusty/main/uefi/grub2-amd64/current/grubnetx64.efi.signed'], 'architectures': ['amd64'], 'readable': 'Grub EFI Netloader', 'archive': 'http://archive.ubuntu.com/', 'lable': 'grub_efi_amd64', 'paths': ['special/grub/amd64/grubnetx64.efi.signed'], 'append': ''}}}
        with open('config.json', 'w') as conf:
            json.dump(config, conf, indent=4)


#Start the actual script
dists = config['distributions']
for dist in dists:
    rels = config['distributions'][dist]['releases']
    for rel in rels:
        architectures = config['distributions'][dist]['architectures']
        for arch in architectures:
            targets = config['distributions'][dist]['targets']
            for target in targets:
                outdir = dist+"/"+rel+"/"+arch+"/"
                installer="installer-"+arch
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                outfile = outdir+target
                print("Downloading "+target+" to "+outfile)
                archive= config['distributions'][dist]['archive']
                os.system("wget "+archive+dist+"/dists/" + rel + "/main/"+installer+"/current/images/netboot/"+dist+"-installer/"+arch+"/"+target+" -O "+outfile+suppress)
for spec in config['special']:
    os.system("wget "+config['special'][spec]['archive'][0]+config['special'][spec]['targets'][0]+" -O "+config['special'][spec]['paths'][0]+suppress)
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
            conffile.write("label "+dist+"_"+rel+"_"+arch+"\n    menu label "+dist+" "+rel+" "+arch+"\n    kernel linux.c32 "+dist+"/"+rel+"/"+arch+"/linux")
            conffile.write(" initrd="+dist+"/"+rel+"/"+arch+"/initrd.gz "+config['distributions'][dist]['append']+"\n\n")
for spec in config['special']:
    print("Adding "+config['special'][spec]['lable']+"...")
    conffile.write("label "+config['special'][spec]['lable']+"\n    menu lable "+config['special'][spec]['readable']+"\n    kernel "+config['special'][spec]['paths'][0]+"\n    append "+config['special'][spec]['append']) 
print("Adding additional bootmenu directives to the end..."
conffile.write(config['append']) # MAYBE: fill with anonymous string[]s for organization?
conffile.close() #technically uneeded unless this is being called directly into another python script
# Example generated entry:
# label debian_jessie_amd64
#     menu label debian jessie amd64
#     kernel debian/jessie/amd64/linux
#     append initrd=debian/jessie/amd64/initrd.img


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
