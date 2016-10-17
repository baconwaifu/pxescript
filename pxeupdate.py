#!/usr/bin/env python3
#Author: slango20
#Description: PXE Netboot Repository tree updater
#Takes options as arrays set in the file
#TODO: set up arguments
#TODO: Config files
#TODO: Add support for non-debian based repository trees (can arch netboot?)
#TODO: find a better way to download files
#TODO low: add per-file progress bar without bloated wget UI
#TODO: Make Modular (add classes for common distros to eliminate the looped distro-specific handling)
#TODO low: threading
#TODO: make core more generic
#DONE: add configuration generator

import os

#Domain for the LAN so that the configuration generator knows what PXE server to use (assuming pxeserver.[domain.com])
domain = "ReplaceMe" # Easily replaceable with "sed -i default 's/ReplaceMe/[domain]/g'"
#added to special download strings to suppress wget output
suppress = " >/dev/null 2>&1"
#amd64 and i386 are the most common
architectures = ["amd64", "i386"]
#Distribution of linux goes here, currently can only handle debian-based
dists = ["debian"]
#Distribution major releases
rels = ["jessie", "sid"]
#Files to get from the repository, must be populated
targets = ["linux", "initrd.gz"]
#Special targets in a wget string followed by a path, need to make a class
special = [["http://archive.ubuntu.com/ubuntu/dists/trusty/main/uefi/grub2-amd64/current/grubnetx64.efi.signed -O special/grub/amd64/grubnetx64.efi.signed", "special/grub/amd64/grubnetx64.efi.signed"]]

for dist in dists:
    for rel in rels:
        for arch in architectures:
            for target in targets:
                outdir = dist+"/"+rel+"/"+arch+"/"
                installer=dist+"-installer" #default, ubuntu changes it
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                outfile = outdir+target
                print("Downloading "+target+" to "+outfile)
                if (dist == "debian"): #Distro specific repository handling, usually just set repository and a few other variables
                    archive="ftp://ftp.us.debian.org/"
                if (dist == "ubuntu"):
                    archive="http://archive.ubuntu.com/"
                    installer=arch+"-installer"
                os.system("wget "+archive+dist+"/dists/" + rel + "/main/"+installer+"/current/images/netboot/"+dist+"-installer/"+arch+"/"+target+" -O "+outfile+" >/dev/null 2>&1")
for i in special:
    os.system("wget "+i[0]+suppress) #Account for array
print("Generating Configuration File...")
conffile = open("default", "w")
conffile.write("default menu.c32\nmenu title PXE Boot System\ntimeout 32\n\n")
for dist in dists:
    for rel in rels:
        for arch in architectures:
            print("Adding "+dist+"_"+rel+"_"+arch+"...")
            conffile.write("lable "+dist+"_"+rel+"_"+arch+"\nmenu label "+dist+" "+rel+" "+arch+"\nkernel http://pxeserver."+domain+"/"+dist+"/"+rel+"/"+arch+"/linux\n")
            conffile.write("append initrd=http://pxeserver."+domain+"/"+dist+"/"+rel+"/"+arch+"/initrd.img\n\n")
# Example generated entry:
# lable debian_jessie_amd64
# menu lable debian jessie amd64
# kernel http://pxeserver.example.com/debian/jessie/amd64/linux
# append initrd=http://pxeserver.example.com/debian/jessie/amd64/initrd.img
