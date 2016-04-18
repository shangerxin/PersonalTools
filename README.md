# PersonalTools
This project will be contain the several kinds of OS enhancement tools

personal website: [http://www.shangerxin.com](http://www.shangerxin.com "my home page")

# Tool list
- treex, it is written in python which will provie enhancement features compare the DOS cmd line tool tree in windows

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

- generate_firefox_userjs.py, a tool used to generate comparison result for different versions of Firefox. The configuration settings could be pull out by another tool script export-firefox-about-config.au3 or export-opened-firefox-config.au3. 
	
	The output of these two script should be placed under the data folder

    +export-opened-firefox-config.au3 and export-opened-firefox-config.au3 is written with [autoit](https://www.autoitscript.com/site/autoit/ "autoit")
	export-opened-firefox-config.au3, will automatic open the Firefox appliction, create a default user profile and pull out the configuration
 
	export-opened-firefox-config.au3, will use current opened Firefox application and then try to pull out all the configuration. 

	After install autoit, just double click to run the script 

- static-js-func-start-end-time contain the hookjs.py it is used to help insert pre process and post process codes for all the functions of JavaScript files. 

    usage: hookjs.py [-h] [-p PATH] [-s START] [-e END]
                     [-f [BLACK_FILES [BLACK_FILES ...]]]
                     [-d [BLACK_DIRS [BLACK_DIRS ...]]]

    A command line JavaScript hook tool for inject start, end codes into every
    JavaScript functions. Currently only support uncompressed EMCScipt 5. Any
    errors will be output into the error.log file. Support macro __FILE__ and
    __LINE__ in the start, end code snippet

    optional arguments:
      -h, --help            show this help message and exit
      -p PATH, --path PATH  The path to the JavaScript file or directory
      -s START, --start START
                            The start code snippet which will be injected at the
                            begin of each function, it also could be a js file
      -e END, --end END     The end code snippet which will be injected at the end
                            of each function, it also could be a js file
      -f [BLACK_FILES [BLACK_FILES ...]], --black-files [BLACK_FILES [BLACK_FILES ...]]
                            Use regex expression to define the black files list,
                            the files will not be hooked
      -d [BLACK_DIRS [BLACK_DIRS ...]], --black-dirs [BLACK_DIRS [BLACK_DIRS ...]]
                            Use regex expression to define the black dirs list,
                            the directory and sub directory will not be searched

    Created by Edwin, Shang(Shang, Erxin), License under GNU LGPLv3. Version 1.7.0

- fast-sync-by-ftp, this tool is design for quickly sync folder from remote directory by FTP. It is expecially useful when IT limited the single TCP/IP connection speed. Currently the server is only suite for window platform because it used a window debugging tool(agestore.exe) to clean the old cache files. Both the client and the server depends on the 7zip to handle the zip file. So it it required to configure the 7z.exe location both for the server and client 

The setup instruction is:
    1. install 7zip on server 
    2. set the 7z.exe location for the server script 
    3. set up a FTP server such as FileZilla and configure the FTP folder location for the server script 
    4. install python27 or build the server with pyinstaller to executable 
    5. start the server 
    6. install 7zip on client
    7. update the 7z.exe location, FTP user/password and server IP and port from the configuration file
    8. done. 
    
Whenever the client request a remote folder the server will first zip the aim location with multiple volume zip files and save the files into the FTP share folder. After that the client will start multiple FTP connections to download each volumens. After all the volumnes is downloaded it could start unzipping base on the command line parameters 

    The client help is:
    usage: sync_client.py [-h] [-b] [-c] [-d] [-f] [-n NUMBER] [-p PORT]
                           [-s SERVER]
                           source output

    Remote sync server, design for quickly sync remote files

    positional arguments:
      source                The source path
      output                The output path

    optional arguments:
      -h, --help            Show this help message and exit
      -b, --buffer          Only zip and save the aim directory to server
      -c, --clean           Delete the downloaded zip files, by default will be kept
      -d, --download        Only download the zipped files without unzip
      -f, --force           The force override download zip files
      -n NUMBER, --number NUMBER
                            The parallel download connection number
      -p PORT, --port PORT  Avaliable port number, default 8081
      -s SERVER, --server SERVER
                            The server name
                            
    Created by Edwin, Shang(Shang, Erxin), License under GNU LGPLv3. Version 1.0.0                   
        