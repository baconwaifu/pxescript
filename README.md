# pxescript
PXE server autoconfiguration and setup script  
Requires a working tftpd and existing pxelinux.0 and support files.  
Note that this places all of the files into what becomes the root of the TFTP server.

## Usage
change config.json (automatically created at first run) to match your configuration.  
Example kernel output: `debian/jessie/amd64/linux`

##TODO
* Support arguments  
* Threaded Downloads  
* Better handling of non-debian distros such as arch (or even grub)  
