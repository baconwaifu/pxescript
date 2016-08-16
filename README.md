# pxescript
PXE server autoconfiguration and setup script  
Requires packages such as pxelinux and tftpd to be installed already.

## Usage
change the variables in the pxeupdate.py to match your configuration. (subject to change fairly quickly)  
Example image tree output: `debian/jessie/amd64/linux`

##TODO
* Support arguments  
* Use Classes to manage different distros (similar to debootstrap scripts)  
* Use seperate config file (probably XML or JSON)  
* Threaded Downloads  
* Actually add pxelinux.cfg and boot.txt generation  
