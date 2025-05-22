# Redis Search Grammar-Based Fuzzer

A powerful and flexible framework for fuzzing Redis Search queries using grammar-based testing techniques. This tool helps identify bugs, edge cases, and performance issues in Redis Search implementations by systematically generating and testing queries across different dialects.

## Features

- **Grammar-Based Query Generation**: Generates queries based on formal grammar rules
- **Multi-Dialect Support**: Tests queries across Redis Search dialects 1-4
- **Controlled Validity**: Generates both valid and invalid queries with configurable ratios
- **Feature Coverage**: Tracks coverage of different Redis Search features
- **Mutation Engine**: Creates invalid queries by mutating valid ones
- **Resource Monitoring**: Tracks CPU, memory, and I/O usage during fuzzing
- **Comprehensive Reporting**: Generates detailed HTML and JSON reports
- **Error Tracking**: Logs and categorizes errors, warnings, and crashes

## Installation

1. Clone the repository:
```bash
git clone [https://github.com/yourusername/redisearch-fuzzer.git](https://github.com/alon-redis/SearchQueryFuzzer)
cd redisearch-fuzzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- Redis 6.0+
- Redis-py 4.5.0+
- Other dependencies listed in `requirements.txt`

## Configuration

The fuzzer can be configured through a YAML file. Here's an example configuration:

```yaml
# Redis connection
redis_host: localhost
redis_port: 6379
redis_password: null

# Generation control
dialect_versions: [1, 2, 3, 4]
valid_query_ratio: 0.7
max_query_length: 1000
max_generation_depth: 20

# Execution control
queries_per_second: 100
timeout_ms: 5000
test_duration_seconds: 3600

# Feature weights
feature_weights:
  full_text: 1.0
  numeric: 0.8
  vector: 0.7
  geo: 0.5
  aggregation: 0.4

# Reporting
log_file: fuzzer_errors.json
log_level: INFO
```

## Usage

### Basic Usage

```python
from redisearch_fuzzer import FuzzerConfig, QueryGenerator, RedisExecutor

# Initialize configuration
config = FuzzerConfig("config.yaml")

# Create query generator
generator = QueryGenerator("grammar/query_grammar.py", config)

# Generate queries
queries = generator.generate_mixed_queries(count=1000, valid_ratio=0.7)

# Execute queries
executor = RedisExecutor(config)
results = executor.execute_query_batch(queries)
```

### Advanced Usage

```python
from redisearch_fuzzer import (
    FuzzerConfig,
    QueryGenerator,
    RedisExecutor,
    ResultValidator,
    FuzzerMonitor,
    ErrorLogger,
    ReportGenerator
)

# Initialize components
config = FuzzerConfig("config.yaml")
generator = QueryGenerator("grammar/query_grammar.py", config)
executor = RedisExecutor(config)
validator = ResultValidator(config)
monitor = FuzzerMonitor()
error_logger = ErrorLogger()
report_generator = ReportGenerator()

# Start monitoring
await monitor.start_monitoring()

# Generate and execute queries
queries = generator.generate_mixed_queries(count=1000)
results = await executor.execute_query_batch(queries)

# Validate results
validation_results = validator.validate_result_batch(results)

# Generate report
report_path = report_generator.generate_report(
    monitor=monitor,
    executor=executor,
    validator=validator,
    error_logger=error_logger,
    config=config.get_all()
)
```

## Project Structure

```
redisearch-fuzzer/
├── config/
│   ├── fuzzer_config.py
│   └── dialect_config.py
├── grammar/
│   ├── parser.py
│   └── rule_expander.py
├── generators/
│   ├── query_generator.py
│   ├── mutation_engine.py
│   └── validity_controller.py
├── execution/
│   ├── redis_executor.py
│   ├── result_validator.py
│   └── monitor.py
├── reporting/
│   ├── error_logger.py
│   └── report_generator.py
├── requirements.txt
└── README.md
```

## Reports

The fuzzer generates three types of reports:

1. **Main Report**: Comprehensive report including execution stats, validation results, and resource usage
2. **Feature Report**: Detailed analysis of feature coverage and feature-specific issues
3. **Performance Report**: Resource usage analysis and performance metrics

Reports are generated in both JSON and HTML formats.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Redis Search team for their excellent documentation
- The fuzzing community for inspiration and best practices

## Support

For issues, feature requests, or questions, please open an issue in the GitHub repository. 
