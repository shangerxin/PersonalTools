;Create by Edwin(Erxin, Shang) 2015-11-28 for export Firefox about:config into plain text

#include <MsgBoxConstants.au3>
#include <FileConstants.au3>
#include <File.au3>

$wait_ms = 500
$wait_timeout = 3000
$max_length = 65536
$output_path = "output.txt"

WinWait("[CLASS:MozillaWindowClass]")
WinActivate("[CLASS:MozillaWindowClass]")

sk("{F6}") ;navigate to about:config
Send("about:config")
sk("{ENTER}")
sk("{ENTER}")

;Select the first item
sk("{TAB}")
sk("{SPACE}")

mm("Before create output file")
Local $output_file = FileOpen($output_path, $FO_OVERWRITE)
If $output_file = 0 Then
   mm("Create output file " & $output_path & " failed!")
   Exit
EndIf

mm("After create output file")

mm("Before get item")
Local $ary[$max_length + 1]
$cur = 0
For $i = 0 To $max_length Step 1
   $ary[$i] = copy_item()
   $cur = $i
   If $i = 0 Then
	  mm($ary[$i])
   EndIf
   If $i > 0 And $ary[$i-1] == $ary[$i] Then
	  ExitLoop
   EndIf
Next

mm("after get item")

mm("before write output $cur = " & $cur)
For $i = 0 To $cur - 1 Step 1
   mm($ary[$i])
   FileWriteLine($output_file, $ary[$i])
Next
FileClose($output_file)
mm("Done")

Func mm($msg)
   ;MsgBox($MB_OK, "info", $msg)
EndFunc

Func copy_item()
   Send("^c")
   Sleep(100)
   Send("{DOWN}")
   Sleep(100)
   Return ClipGet()
EndFunc


Func sk($msg)
   Send($msg)
   Sleep($wait_ms)
EndFunc




