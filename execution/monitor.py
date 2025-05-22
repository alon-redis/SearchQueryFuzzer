import time
import psutil
import asyncio
from typing import List, Dict, Optional, Set, Tuple, Any, Union
from datetime import datetime


class FuzzerMonitor:
    """Monitors the fuzzer's execution and resource usage."""
    
    def __init__(self):
        """Initialize the fuzzer monitor."""
        self.start_time = time.time()
        self.metrics_history: List[Dict[str, Any]] = []
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self, interval_seconds: float = 1.0) -> None:
        """Start monitoring the fuzzer.
        
        Args:
            interval_seconds: Interval between metric collection in seconds.
        """
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(
            self._monitor_loop(interval_seconds)
        )
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring the fuzzer."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self, interval_seconds: float) -> None:
        """Main monitoring loop.
        
        Args:
            interval_seconds: Interval between metric collection in seconds.
        """
        while self.is_monitoring:
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)
            await asyncio.sleep(interval_seconds)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics.
        
        Returns:
            Dictionary containing current metrics.
        """
        process = psutil.Process()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "elapsed_time": time.time() - self.start_time,
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_info": {
                "rss": process.memory_info().rss,
                "vms": process.memory_info().vms
            },
            "io_counters": {
                "read_bytes": process.io_counters().read_bytes,
                "write_bytes": process.io_counters().write_bytes
            },
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, "num_fds") else None
        }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics.
        
        Returns:
            Dictionary containing the most recent metrics.
        """
        if not self.metrics_history:
            return self._collect_metrics()
        return self.metrics_history[-1]
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get the complete metrics history.
        
        Returns:
            List of metric dictionaries.
        """
        return self.metrics_history
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from the metrics history.
        
        Returns:
            Dictionary containing summary statistics.
        """
        if not self.metrics_history:
            return {
                "total_time": 0,
                "avg_cpu_percent": 0,
                "avg_memory_percent": 0,
                "max_memory_usage": 0,
                "total_io_read": 0,
                "total_io_write": 0
            }
        
        cpu_percents = [m["cpu_percent"] for m in self.metrics_history]
        memory_percents = [m["memory_percent"] for m in self.metrics_history]
        memory_usage = [m["memory_info"]["rss"] for m in self.metrics_history]
        io_read = [m["io_counters"]["read_bytes"] for m in self.metrics_history]
        io_write = [m["io_counters"]["write_bytes"] for m in self.metrics_history]
        
        return {
            "total_time": self.metrics_history[-1]["elapsed_time"],
            "avg_cpu_percent": sum(cpu_percents) / len(cpu_percents),
            "avg_memory_percent": sum(memory_percents) / len(memory_percents),
            "max_memory_usage": max(memory_usage),
            "total_io_read": io_read[-1] - io_read[0],
            "total_io_write": io_write[-1] - io_write[0]
        }
    
    def clear_history(self) -> None:
        """Clear the metrics history."""
        self.metrics_history.clear()
        self.start_time = time.time()
    
    def get_resource_warnings(self) -> List[Dict[str, Any]]:
        """Get warnings about resource usage.
        
        Returns:
            List of dictionaries containing resource warnings.
        """
        warnings = []
        
        if not self.metrics_history:
            return warnings
        
        latest_metrics = self.metrics_history[-1]
        
        # Check CPU usage
        if latest_metrics["cpu_percent"] > 90:
            warnings.append({
                "type": "high_cpu",
                "value": latest_metrics["cpu_percent"],
                "threshold": 90
            })
        
        # Check memory usage
        if latest_metrics["memory_percent"] > 80:
            warnings.append({
                "type": "high_memory",
                "value": latest_metrics["memory_percent"],
                "threshold": 80
            })
        
        # Check I/O rate
        if len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            time_diff = latest_metrics["elapsed_time"] - prev_metrics["elapsed_time"]
            
            read_rate = (latest_metrics["io_counters"]["read_bytes"] -
                        prev_metrics["io_counters"]["read_bytes"]) / time_diff
            write_rate = (latest_metrics["io_counters"]["write_bytes"] -
                         prev_metrics["io_counters"]["write_bytes"]) / time_diff
            
            if read_rate > 1e6:  # 1 MB/s
                warnings.append({
                    "type": "high_read_rate",
                    "value": read_rate,
                    "threshold": 1e6
                })
            
            if write_rate > 1e6:  # 1 MB/s
                warnings.append({
                    "type": "high_write_rate",
                    "value": write_rate,
                    "threshold": 1e6
                })
        
        return warnings
    
    def get_metrics_trend(self, metric_name: str, window_size: int = 10) -> List[float]:
        """Get the trend of a specific metric.
        
        Args:
            metric_name: Name of the metric to track.
            window_size: Number of recent values to return.
            
        Returns:
            List of recent metric values.
        """
        if not self.metrics_history:
            return []
        
        values = []
        for metrics in self.metrics_history[-window_size:]:
            if metric_name in metrics:
                values.append(metrics[metric_name])
            elif "." in metric_name:
                # Handle nested metrics (e.g., "memory_info.rss")
                parts = metric_name.split(".")
                value = metrics
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    values.append(value)
        
        return values
