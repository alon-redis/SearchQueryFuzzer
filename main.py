#!/usr/bin/env python3

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

from config.fuzzer_config import FuzzerConfig
from grammar.parser import GrammarParser
from grammar.rule_expander import RuleExpander
from generators.query_generator import QueryGenerator
from generators.mutation_engine import MutationEngine
from generators.validity_controller import ValidityController
from execution.redis_executor import RedisExecutor
from execution.result_validator import ResultValidator
from execution.monitor import FuzzerMonitor
from reporting.error_logger import ErrorLogger
from reporting.report_generator import ReportGenerator


class RedisSearchFuzzer:
    """Main class for the Redis Search Grammar-Based Fuzzer."""
    
    def __init__(self, config_path: str):
        """Initialize the fuzzer.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config = FuzzerConfig(config_path)
        self.error_logger = ErrorLogger()
        self.monitor = FuzzerMonitor()
        
        # Initialize components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize all fuzzer components."""
        try:
            # Initialize grammar components
            self.parser = GrammarParser("grammar/query_grammar.py")
            self.expander = RuleExpander(self.parser, self.config.get("max_generation_depth"))
            
            # Initialize generators
            self.query_generator = QueryGenerator(
                "grammar/query_grammar.py",
                self.config.get("dialect_config"),
                self.config.get("max_generation_depth")
            )
            self.mutation_engine = MutationEngine(self.config.get("dialect_config"))
            self.validity_controller = ValidityController(
                self.config.get("dialect_config"),
                self.mutation_engine
            )
            
            # Initialize execution components
            self.executor = RedisExecutor(self.config)
            self.validator = ResultValidator(self.config.get("dialect_config"))
            
            # Initialize reporting
            self.report_generator = ReportGenerator()
            
        except Exception as e:
            self.error_logger.log_error(
                "initialization_error",
                f"Failed to initialize fuzzer components: {str(e)}"
            )
            raise
    
    async def run(self) -> None:
        """Run the fuzzer."""
        try:
            # Start monitoring
            await self.monitor.start_monitoring()
            
            # Generate queries
            queries = self.query_generator.generate_mixed_queries(
                count=self.config.get("queries_per_batch"),
                valid_ratio=self.config.get("valid_query_ratio")
            )
            
            # Execute queries
            results = await self.executor.execute_query_batch(queries)
            
            # Validate results
            validation_results = self.validator.validate_result_batch(results)
            
            # Generate reports
            self._generate_reports()
            
        except Exception as e:
            self.error_logger.log_error(
                "execution_error",
                f"Fuzzer execution failed: {str(e)}"
            )
            raise
        
        finally:
            # Stop monitoring
            await self.monitor.stop_monitoring()
    
    def _generate_reports(self) -> None:
        """Generate all fuzzer reports."""
        try:
            # Generate main report
            self.report_generator.generate_report(
                monitor=self.monitor,
                executor=self.executor,
                validator=self.validator,
                error_logger=self.error_logger,
                config=self.config.get_all()
            )
            
            # Generate feature report
            self.report_generator.generate_feature_report(
                validator=self.validator,
                error_logger=self.error_logger
            )
            
            # Generate performance report
            self.report_generator.generate_performance_report(
                monitor=self.monitor,
                executor=self.executor
            )
            
        except Exception as e:
            self.error_logger.log_error(
                "reporting_error",
                f"Failed to generate reports: {str(e)}"
            )
            raise


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Redis Search Grammar-Based Fuzzer"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config/default_config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--dialect",
        type=int,
        choices=[1, 2, 3, 4],
        help="Specific dialect version to test"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        help="Test duration in seconds"
    )
    
    parser.add_argument(
        "--queries",
        type=int,
        help="Number of queries to generate"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for the fuzzer.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Create and run fuzzer
        fuzzer = RedisSearchFuzzer(args.config)
        
        # Override config with command line arguments
        if args.dialect:
            fuzzer.config.set("dialect_versions", [args.dialect])
        if args.duration:
            fuzzer.config.set("test_duration_seconds", args.duration)
        if args.queries:
            fuzzer.config.set("queries_per_batch", args.queries)
        
        # Run the fuzzer
        asyncio.run(fuzzer.run())
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
