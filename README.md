# pxescript
PXE server autoconfiguration and setup script
Requires packages such as pxelinux and tftpd to be installed already.

# Usage
change the variables in the pxeupdate.py to match your configuration. (subject to change fairly quickly)
File output will produce a folder tree matching $dist:$release:$arch

#TODO
Support arguments
Use Classes to manage different distros (similar to debootstrap scripts)
Add seperate config file (probably XML or JSON)
Threaded Downloads
actually add pxelinux.cfg and boot.txt generation
