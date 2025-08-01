from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import App

import customtkinter as ctk
import time
from lib.Navigation import NavigationPage

# Try to import performance monitoring
try:
    from lib.PerformanceMonitor import get_performance_monitor, start_performance_monitoring
    PERFORMANCE_MONITORING = True
except ImportError:
    PERFORMANCE_MONITORING = False

class DebugPage(NavigationPage):

    def __init__(self, navigator, appRoot: 'App', master, **kwargs):
        super().__init__(navigator, master, title="Debug", **kwargs)
        self.appRoot: 'App' = appRoot
        
        self.performance_monitor = None
        if PERFORMANCE_MONITORING:
            self.performance_monitor = get_performance_monitor()
            start_performance_monitoring()
        
        self._initUI()
        self._initCommands()
        
        # Start updating performance display
        if PERFORMANCE_MONITORING:
            self._updatePerformanceDisplay()

    def _initUI(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Original debug title
        self.ui.add(ctk.CTkLabel, "title",
                    text="🐛 Debug & Performance",
                    font=(self.appRoot.FONT_NAME, 24)
                    ).grid(row=0, column=0, columnspan=10, padx=20, pady=20, sticky="nw")

        # Performance monitoring section
        if PERFORMANCE_MONITORING:
            perf_frame = self.ui.add(ctk.CTkFrame, "perf_frame",
                                    corner_radius=12
                                    ).grid(row=1, column=0, columnspan=10, padx=20, pady=(0, 20), sticky="nsew")
            
            perf_frame.getInstance().grid_columnconfigure(0, weight=1)
            perf_frame.getInstance().grid_rowconfigure(1, weight=1)

            self.ui.add(ctk.CTkLabel, "perf_title",
                        root=perf_frame.getInstance(),
                        text="System Performance Monitor",
                        font=(self.appRoot.FONT_NAME, 18, "bold")
                        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
            
            self.ui.add(ctk.CTkTextbox, "perf_display",
                        root=perf_frame.getInstance(),
                        height=200,
                        font=(self.appRoot.FONT_NAME, 10)
                        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        else:
            self.ui.add(ctk.CTkLabel, "no_perf",
                        text="Performance monitoring not available (psutil not installed)",
                        font=(self.appRoot.FONT_NAME, 14)
                        ).grid(row=1, column=0, columnspan=10, padx=20, pady=20, sticky="w")

    def _initCommands(self):
        pass

    def _updatePerformanceDisplay(self):
        """Update performance display every second"""
        if not PERFORMANCE_MONITORING or not self.performance_monitor:
            return
            
        try:
            summary = self.performance_monitor.get_performance_summary()
            
            # Get additional system info
            import threading
            import os
            
            # Try to get CPU affinity (safely)
            try:
                import psutil
                process = psutil.Process()
                try:
                    cpu_affinity = list(process.cpu_affinity())
                except (psutil.AccessDenied, OSError, AttributeError):
                    cpu_affinity = "Not available"
                    
                cpu_count = psutil.cpu_count()
                
                # Get per-core CPU usage
                cpu_per_core = psutil.cpu_percent(percpu=True)
            except ImportError:
                cpu_affinity = "psutil not available"
                cpu_count = "Unknown" 
                cpu_per_core = []
            except Exception:
                cpu_affinity = "Error reading"
                cpu_count = "Unknown"
                cpu_per_core = []
            
            display_text = f"""System Performance Monitor - {time.strftime('%H:%M:%S')}

CPU & Memory:
  Overall CPU Usage: {summary['cpu_usage']:.1f}%
  Memory Usage: {summary['memory_usage']:.1f}%
  CPU Count: {cpu_count}
  CPU Affinity: {cpu_affinity}

Per-Core Usage:"""
            
            for i, usage in enumerate(cpu_per_core):
                core_role = "UI" if i in [0, 1] else "LED"
                display_text += f"\n  Core {i} ({core_role}): {usage:.1f}%"
            
            display_text += f"""

LED Processing:
  LED FPS: {summary['led_fps']:.1f} (target: 60)
  Frame Time: {summary['led_frame_time_ms']:.1f} ms (target: <16.7ms)

Threading:
  Process ID: {summary['process_id']}
  Active Threads: {summary['thread_count']}
"""
            
            textbox = self.ui.get("perf_display")
            if textbox and textbox.getInstance():
                textbox.getInstance().delete("0.0", "end")
                textbox.getInstance().insert("0.0", display_text)
                
        except Exception as e:
            print(f"Performance display update error: {e}")
        
        # Schedule next update
        self.appRoot.after(1000, self._updatePerformanceDisplay)
