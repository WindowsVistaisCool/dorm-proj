import threading
import time
import psutil
import os
from typing import Optional

class PerformanceMonitor:
    """
    Monitors system performance and LED processing metrics
    """
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Metrics
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.led_fps = 0.0
        self.led_frame_time = 0.0
        self.ui_responsiveness = 0.0
        
        # Frame timing for LED FPS calculation
        self.led_frame_times = []
        self.max_frame_samples = 60
        
        # CPU affinity info
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """Start performance monitoring in a separate thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
    def record_led_frame(self, frame_time: float):
        """Record LED frame processing time for FPS calculation"""
        current_time = time.time()
        self.led_frame_times.append((current_time, frame_time))
        
        # Keep only recent samples
        cutoff_time = current_time - 1.0  # Keep 1 second of samples
        self.led_frame_times = [(t, ft) for t, ft in self.led_frame_times if t > cutoff_time]
        
        # Calculate FPS and average frame time
        if len(self.led_frame_times) > 1:
            time_span = self.led_frame_times[-1][0] - self.led_frame_times[0][0]
            if time_span > 0:
                self.led_fps = len(self.led_frame_times) / time_span
                self.led_frame_time = sum(ft for _, ft in self.led_frame_times) / len(self.led_frame_times)
                
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # CPU and memory usage
                self.cpu_usage = psutil.cpu_percent(interval=None)
                self.memory_usage = psutil.virtual_memory().percent
                
                # Check CPU affinity (safely)
                try:
                    affinity = self.process.cpu_affinity()
                    # Log affinity info if needed, but don't force changes
                except (psutil.AccessDenied, AttributeError, OSError):
                    # CPU affinity not available or not permitted
                    pass
                    
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                
            time.sleep(self.update_interval)
            
    def get_performance_summary(self) -> dict:
        """Get current performance metrics"""
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'led_fps': self.led_fps,
            'led_frame_time_ms': self.led_frame_time * 1000,
            'process_id': os.getpid(),
            'thread_count': threading.active_count()
        }
        
    def print_performance_summary(self):
        """Print performance summary to console"""
        summary = self.get_performance_summary()
        print(f"Performance: CPU: {summary['cpu_usage']:.1f}% | "
              f"Memory: {summary['memory_usage']:.1f}% | "
              f"LED FPS: {summary['led_fps']:.1f} | "
              f"Frame Time: {summary['led_frame_time_ms']:.1f}ms")

# Global instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_performance_monitoring():
    """Start performance monitoring"""
    get_performance_monitor().start_monitoring()

def stop_performance_monitoring():
    """Stop performance monitoring"""
    if _performance_monitor:
        _performance_monitor.stop_monitoring()

def record_led_frame(frame_time: float):
    """Record LED frame processing time"""
    if _performance_monitor:
        _performance_monitor.record_led_frame(frame_time)
