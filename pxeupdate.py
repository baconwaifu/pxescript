#!/usr/bin/env python3
#Author: slango20
#Description: PXE Netboot Repository tree updater
#Takes options as arrays set in the file
#TODO: set up arguments
#TODO: Add support for non-debian based repository trees (can arch netboot?)
#TODO: find a better way to download files
#TODO: add per-file progress bar without bloated wget UI
#TODO: Make Modular (add classes for common distros to eliminate the looped distro-specific handling)
#TODO: threading
#TODO: make core more generic
#TODO: Add configuration generator

import os

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
#Special targets in a wget string, need to make a class
special = ["http://archive.ubuntu.com/ubuntu/dists/trusty/main/uefi/grub2-amd64/current/grubnetx64.efi.signed -O special/grub/amd64/grubnetx64.efi.signed"]

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
                if (dist == "debian"): #Distro specific repository handling, usually just set repository
                    archive="ftp://ftp.us.debian.org/"
                if (dist == "ubuntu"):
                    archive="http://archive.ubuntu.com/"
                    installer=arch+"-installer"
                os.system("wget "+archive+dist+"/dists/" + rel + "/main/"+installer+"/current/images/netboot/"+dist+"-installer/"+arch+"/"+target+" -O "+outfile+" >/dev/null 2>&1")
for i in special:
    os.system("wget "+i+suppress)
