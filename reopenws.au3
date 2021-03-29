$title = "Evaluation License Expired"
$wait_ms = 100
$webstorm = "C:\Program Files (x86)\JetBrains\WebStorm 2016.1.1\bin\WebStorm.exe"

While True
   If Not ProcessExists("WebStorm.exe") Then
	  Run($webstorm)
   EndIf
   WinWait($title)
   WinActivate($title)
   Send("{TAB}")
   Send("{TAB}")
   Send("{SPACE}")

   ;ProcessClose("WebStorm.exe")
   ;Run($webstorm)

   If ProcessExists("WebStorm.exe") Then
	  WinWait($title)
	  WinActivate($title)
	  send("{TAB}")
	  send("{SPACE}")
	  ProcessClose("WebStorm.exe")
	  Run($webstorm)
	  Sleep(1000)
   EndIf
WEnd