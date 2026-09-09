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
import win32serviceutil
import win32service
import win32event
import servicemanager
import threading

# Add project root to path so imports work inside service
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class VPNAnalyzerService(win32serviceutil.ServiceFramework):
    _svc_name_         = "VPNAnalyzerService"
    _svc_display_name_ = "IPsec VPN Analyzer Service"
    _svc_description_  = "Monitors IPsec VPN traffic and provides analysis via localhost:8000"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.server = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
        # Stop uvicorn server gracefully
        if self.server:
            self.server.should_exit = True
            
        # Signal our background threads to stop
        try:
            from backend.core.shared import stop_event as backend_stop
            backend_stop.set()
        except Exception:
            pass

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        self._run()

    def _run(self):
        import uvicorn
        from backend.api.main import app
        
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
        self.server = uvicorn.Server(config)
        
        # Run uvicorn in a separate thread so we can wait on the Windows stop event
        t = threading.Thread(target=self.server.run, daemon=True)
        t.start()
        
        # Wait until stop signal from Windows Service Control Manager
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
