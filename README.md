# PersonalTools
This project will be contain the several kinds of OS enhancement tools

personal website: [http://www.shangerxin.com](http://www.shangerxin.com "my home page")

# Tool list
	+ treex, it is written in python which will provie enhancement features compare the DOS cmd line tool tree in windows

	usage: treex.py [-h] [-f] [-d DEPTH] [-m] [-e] path
	
	A Cmd Line Tool for Graphically displays the folder structure of a drive or
	path
	
	positional arguments:
	  path
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -f, --file            Display the names of the files in each folder
	  -d DEPTH, --depth DEPTH
	                        Display the depth number
	  -m, --mark            Mark the item is file or directory
	  -e, --ellipsis        Mark the next sub-item with ellipsis
	
	Create by Edwin, Shang(Shang, Erxin) License under MIT. Version 1.0.0

	example:
	D:\PersonalTools>python treex.py D:\Project\TC_trunk\app\Platform\Web2UI\xulrunner-sdk -d 3 -m
	Folder path listing
	D:\Project\TC_trunk\app\Platform\Web2UI\xulrunner-sdk
	[d]\---win32
	[d]    +---bin
	[d]    |   +---chrome
	[d]    |   +---components
	[d]    |   +---defaults
	[d]    |   +---dictionaries
	[d]    |   +---gmp-clearkey
	[d]    |   +---gmp-fake
	[d]    |   +---gmp-fakeopenh264
	[d]    |   +---hyphenation
	[d]    |   +---modules
	[d]    |   \---res
	[d]    +---host
	[d]    |   \---bin
	[d]    +---idl
	[d]    +---include
	[d]    |   +---angle
	[d]    |   +---cairo
	[d]    |   +---cubeb
	[d]    |   +---dbm
	[d]    |   +---demuxer
	[d]    |   +---gfxipc
	[d]    |   +---google
	[d]    |   +---graphite2
	[d]    |   +---gtest
	[d]    |   +---harfbuzz
	[d]    |   +---ipc
	[d]    |   +---js
	[d]    |   +---kiss_fft
	[d]    |   +---mozilla
	[d]    |   +---mp4_demuxer
	[d]    |   +---mtransport
	[d]    |   +---nestegg
	[d]    |   +---nspr
	[d]    |   +---nss
	[d]    |   +---ogg
	[d]    |   +---opus
	[d]    |   +---skia
	[d]    |   +---snappy
	[d]    |   +---soundtouch
	[d]    |   +---speex
	[d]    |   +---theora
	[d]    |   +---vorbis
	[d]    |   \---vpx
	[d]    +---lib
	[d]    \---sdk
    [d]        \---win32_release

	+ generate_firefox_userjs.py, a tool used to generate comparison result for different versions of Firefox. The configuration settings could be pull out by another tool script export-firefox-about-config.au3 or export-opened-firefox-config.au3. 
	
	The output of these two script should be placed under the data folder

	+ export-opened-firefox-config.au3 and export-opened-firefox-config.au3 is written with [autoit](https://www.autoitscript.com/site/autoit/ "autoit")
	export-opened-firefox-config.au3, will automatic open the Firefox appliction, create a default user profile and pull out the configuration
 
	export-opened-firefox-config.au3, will use current opened Firefox application and then try to pull out all the configuration. 

	After install autoit, just double click to run the script 

	+ hookjs.py, under the static-js-func-start-end-time folder. it is used to help insert pre process and post process codes for all the functions of JavaScript files. 
	