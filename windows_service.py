"""
Register as Windows Service:
  python windows_service.py install
  python windows_service.py start
  python windows_service.py stop
  python windows_service.py remove

Requires: pip install pywin32
After install: python Scripts/pywin32_postinstall.py -install
"""

import sys
import os
import subprocess
import win32serviceutil
import win32service
import win32event
import servicemanager

# Add project root to path so imports work inside service
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class VPNAnalyzerService(win32serviceutil.ServiceFramework):
    _svc_name_         = "VPNAnalyzerService"
    _svc_display_name_ = "VPN Analyzer Background Service"
    _svc_description_  = "Monitors IPsec VPN traffic and provides analysis via localhost:8000"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=10)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        self._run()

    def _run(self):
        # Run uvicorn as subprocess — works with PyInstaller too
        cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.api.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "info"
        ]
        self.process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        # Wait until stop signal
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Called by SCM directly
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VPNAnalyzerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # CLI: install / start / stop / remove
        win32serviceutil.HandleCommandLine(VPNAnalyzerService)
