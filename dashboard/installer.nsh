!macro customInstall
  DetailPrint "Launching Npcap Network Driver Setup... Please complete the installation."
  ExecWait '"$INSTDIR\resources\npcap-installer.exe"'
  DetailPrint "Registering VPN Analyzer Background Service..."
  # ExecWait does not show a console window
  nsExec::ExecToLog '"$INSTDIR\resources\backend\backend.exe" install'
  DetailPrint "Starting VPN Analyzer Background Service..."
  nsExec::ExecToLog '"$INSTDIR\resources\backend\backend.exe" start'
!macroend

!macro customUnInstall
  DetailPrint "Stopping VPN Analyzer Background Service..."
  nsExec::ExecToLog '"$INSTDIR\resources\backend\backend.exe" stop'
  DetailPrint "Removing VPN Analyzer Background Service..."
  nsExec::ExecToLog '"$INSTDIR\resources\backend\backend.exe" remove'
!macroend
