import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any, Union
from ..execution.monitor import FuzzerMonitor
from ..execution.redis_executor import RedisExecutor
from ..execution.result_validator import ResultValidator
from .error_logger import ErrorLogger


class ReportGenerator:
    """Generates comprehensive reports of fuzzing results."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the report generator.
        
        Args:
            output_dir: Directory to store report files.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        monitor: FuzzerMonitor,
        executor: RedisExecutor,
        validator: ResultValidator,
        error_logger: ErrorLogger,
        config: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive fuzzing report.
        
        Args:
            monitor: Fuzzer monitor instance.
            executor: Redis executor instance.
            validator: Result validator instance.
            error_logger: Error logger instance.
            config: Fuzzer configuration.
            
        Returns:
            Path to the generated report file.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "configuration": config,
            "summary": self._generate_summary(
                monitor, executor, validator, error_logger
            ),
            "execution_stats": executor.get_execution_stats(),
            "validation_stats": validator.get_validation_stats(),
            "resource_usage": monitor.get_summary_stats(),
            "error_summary": error_logger.get_error_summary(),
            "feature_coverage": validator.get_feature_coverage(),
            "validation_errors": validator.get_validation_errors(),
            "unexpected_successes": validator.get_unexpected_successes(),
            "unexpected_failures": validator.get_unexpected_failures(),
            "slow_queries": executor.get_slow_queries(),
            "resource_warnings": monitor.get_resource_warnings()
        }
        
        # Save report
        report_path = self.output_dir / f"fuzzer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        html_path = self._generate_html_report(report, report_path)
        
        return str(html_path)
    
    def _generate_summary(
        self,
        monitor: FuzzerMonitor,
        executor: RedisExecutor,
        validator: ResultValidator,
        error_logger: ErrorLogger
    ) -> Dict[str, Any]:
        """Generate a summary of fuzzing results.
        
        Args:
            monitor: Fuzzer monitor instance.
            executor: Redis executor instance.
            validator: Result validator instance.
            error_logger: Error logger instance.
            
        Returns:
            Dictionary containing summary information.
        """
        exec_stats = executor.get_execution_stats()
        val_stats = validator.get_validation_stats()
        resource_stats = monitor.get_summary_stats()
        error_summary = error_logger.get_error_summary()
        
        return {
            "total_queries": exec_stats["total_queries"],
            "success_rate": exec_stats["success_rate"],
            "validation_match_rate": val_stats["match_rate"],
            "total_errors": error_summary["total_errors"],
            "total_warnings": error_summary["total_warnings"],
            "total_crashes": error_summary["total_crashes"],
            "total_execution_time": resource_stats["total_time"],
            "average_cpu_usage": resource_stats["avg_cpu_percent"],
            "average_memory_usage": resource_stats["avg_memory_percent"],
            "max_memory_usage": resource_stats["max_memory_usage"]
        }
    
    def _generate_html_report(self, report: Dict[str, Any], json_path: Path) -> Path:
        """Generate an HTML version of the report.
        
        Args:
            report: Report data dictionary.
            json_path: Path to the JSON report file.
            
        Returns:
            Path to the generated HTML report.
        """
        html_path = json_path.with_suffix(".html")
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redis Search Fuzzer Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .section { margin-bottom: 20px; }
                .section h2 { color: #333; }
                .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
                .error { color: #d32f2f; }
                .warning { color: #f57c00; }
                .success { color: #388e3c; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f5f5f5; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Redis Search Fuzzer Report</h1>
            <p>Generated at: {timestamp}</p>
            
            <div class="section">
                <h2>Summary</h2>
                <div class="summary">
                    <p>Total Queries: {total_queries}</p>
                    <p>Success Rate: {success_rate:.2%}</p>
                    <p>Validation Match Rate: {validation_match_rate:.2%}</p>
                    <p>Total Errors: {total_errors}</p>
                    <p>Total Warnings: {total_warnings}</p>
                    <p>Total Crashes: {total_crashes}</p>
                    <p>Total Execution Time: {total_time:.2f} seconds</p>
                    <p>Average CPU Usage: {avg_cpu:.2f}%</p>
                    <p>Average Memory Usage: {avg_memory:.2f}%</p>
                    <p>Maximum Memory Usage: {max_memory} bytes</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Feature Coverage</h2>
                <table>
                    <tr>
                        <th>Feature</th>
                        <th>Coverage</th>
                    </tr>
                    {feature_coverage_rows}
                </table>
            </div>
            
            <div class="section">
                <h2>Validation Errors</h2>
                <table>
                    <tr>
                        <th>Query</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Errors</th>
                    </tr>
                    {validation_error_rows}
                </table>
            </div>
            
            <div class="section">
                <h2>Slow Queries</h2>
                <table>
                    <tr>
                        <th>Query</th>
                        <th>Execution Time (ms)</th>
                    </tr>
                    {slow_query_rows}
                </table>
            </div>
            
            <div class="section">
                <h2>Resource Warnings</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Value</th>
                        <th>Threshold</th>
                    </tr>
                    {resource_warning_rows}
                </table>
            </div>
        </body>
        </html>
        """
        
        # Generate table rows
        feature_coverage_rows = "\n".join(
            f"<tr><td>{feature}</td><td>{coverage:.2%}</td></tr>"
            for feature, coverage in report["feature_coverage"].items()
        )
        
        validation_error_rows = "\n".join(
            f"<tr><td>{error['query']}</td><td>{error['expected_valid']}</td>"
            f"<td>{error['actual_valid']}</td><td>{', '.join(error['errors'])}</td></tr>"
            for error in report["validation_errors"]
        )
        
        slow_query_rows = "\n".join(
            f"<tr><td>{query['query']}</td><td>{query['execution_time']}</td></tr>"
            for query in report["slow_queries"]
        )
        
        resource_warning_rows = "\n".join(
            f"<tr><td>{warning['type']}</td><td>{warning['value']}</td>"
            f"<td>{warning['threshold']}</td></tr>"
            for warning in report["resource_warnings"]
        )
        
        # Format the template
        html_content = html_template.format(
            timestamp=report["timestamp"],
            total_queries=report["summary"]["total_queries"],
            success_rate=report["summary"]["success_rate"],
            validation_match_rate=report["summary"]["validation_match_rate"],
            total_errors=report["summary"]["total_errors"],
            total_warnings=report["summary"]["total_warnings"],
            total_crashes=report["summary"]["total_crashes"],
            total_time=report["summary"]["total_execution_time"],
            avg_cpu=report["summary"]["average_cpu_usage"],
            avg_memory=report["summary"]["average_memory_usage"],
            max_memory=report["summary"]["max_memory_usage"],
            feature_coverage_rows=feature_coverage_rows,
            validation_error_rows=validation_error_rows,
            slow_query_rows=slow_query_rows,
            resource_warning_rows=resource_warning_rows
        )
        
        # Save the HTML report
        with open(html_path, "w") as f:
            f.write(html_content)
        
        return html_path
    
    def generate_feature_report(
        self,
        validator: ResultValidator,
        error_logger: ErrorLogger
    ) -> str:
        """Generate a feature-specific report.
        
        Args:
            validator: Result validator instance.
            error_logger: Error logger instance.
            
        Returns:
            Path to the generated report file.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "feature_coverage": validator.get_feature_coverage(),
            "missing_features": validator.get_missing_features(),
            "least_covered_features": validator.get_least_covered_features(),
            "feature_errors": self._get_feature_errors(error_logger)
        }
        
        # Save report
        report_path = self.output_dir / f"feature_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def _get_feature_errors(self, error_logger: ErrorLogger) -> Dict[str, List[Dict[str, Any]]]:
        """Get errors grouped by feature.
        
        Args:
            error_logger: Error logger instance.
            
        Returns:
            Dictionary mapping features to their errors.
        """
        feature_errors = {}
        
        for error in error_logger.errors:
            if "feature" in error.get("details", {}):
                feature = error["details"]["feature"]
                if feature not in feature_errors:
                    feature_errors[feature] = []
                feature_errors[feature].append(error)
        
        return feature_errors
    
    def generate_performance_report(
        self,
        monitor: FuzzerMonitor,
        executor: RedisExecutor
    ) -> str:
        """Generate a performance-specific report.
        
        Args:
            monitor: Fuzzer monitor instance.
            executor: Redis executor instance.
            
        Returns:
            Path to the generated report file.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "resource_usage": monitor.get_summary_stats(),
            "slow_queries": executor.get_slow_queries(),
            "resource_warnings": monitor.get_resource_warnings(),
            "execution_stats": executor.get_execution_stats(),
            "metrics_trends": {
                "cpu": monitor.get_metrics_trend("cpu_percent"),
                "memory": monitor.get_metrics_trend("memory_percent"),
                "io_read": monitor.get_metrics_trend("io_counters.read_bytes"),
                "io_write": monitor.get_metrics_trend("io_counters.write_bytes")
            }
        }
        
        # Save report
        report_path = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
