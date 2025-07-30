# Weather Data Streaming Processor

A Python-based streaming data processing system designed to aggregate weather station samples and provide real-time snapshots of weather conditions across multiple stations.

## Overview

This project implements a robust streaming data processor that handles heterogeneous message types including weather samples and control commands. The system is designed to operate as part of a larger data pipeline, processing JSON messages from STDIN and outputting aggregated results to STDOUT.

## Architecture

### Core Components

- **Message Processor**: Handles weather samples and control messages
- **State Management**: Maintains aggregated weather data per station
- **Generator-based Processing**: Ensures memory-efficient streaming
- **Error Handling**: Comprehensive validation and error reporting

### Data Flow

```
STDIN (JSON messages) → process_events() → STDOUT (JSON results)
```

## Features

### Weather Sample Processing
- **Real-time aggregation**: Tracks high and low temperatures per station
- **Timestamp management**: Maintains chronological order and latest timestamps
- **Multi-station support**: Handles data from multiple weather stations simultaneously

### Control Message Support
- **Snapshot requests**: Generate aggregated weather statistics
- **Reset functionality**: Clear all station data and confirm operations
- **Extensible design**: Easy to add new control commands

### Performance Optimizations
- **Memory efficient**: Generator-based processing prevents memory overflow
- **Lazy evaluation**: Processes data as it arrives
- **Minimal state**: Only stores essential aggregated data

## Implementation Details

### Message Types

#### Weather Samples
```json
{
  "type": "sample",
  "stationName": "Foster Weather Station",
  "timestamp": 1672531200000,
  "temperature": 37.1
}
```

#### Control Messages
```json
{
  "type": "control",
  "command": "snapshot"
}
```

### Output Formats

#### Snapshot Response
```json
{
  "type": "snapshot",
  "asOf": 1672531200000,
  "stations": {
    "Foster Weather Station": {"high": 37.1, "low": 32.5}
  }
}
```

#### Reset Confirmation
```json
{
  "type": "reset",
  "asOf": 1672531200000
}
```

## Technical Approach

### State Management
- Uses `defaultdict` for efficient station data tracking
- Maintains separate high/low temperature records per station
- Tracks latest timestamp for accurate `asOf` values

### Error Handling Strategy
- Validates all required fields in weather samples
- Handles unknown message types with informative errors
- Provides specific error messages for debugging

### Memory Management
- Generator function ensures streaming processing
- No accumulation of input data in memory
- Efficient data structures for state tracking

## Testing Strategy

### Comprehensive Test Coverage
- **Unit tests**: 15 test cases covering all functionality
- **Edge cases**: Empty data, invalid messages, boundary conditions
- **Integration tests**: Full JSON input/output validation
- **Performance tests**: Memory usage and generator behavior

### Test Categories
1. **Basic functionality**: Weather sample processing
2. **Control commands**: Snapshot and reset operations
3. **Error handling**: Invalid inputs and edge cases
4. **Multi-station scenarios**: Complex data aggregation
5. **State management**: Reset and data clearing

## Usage Examples

### Basic Weather Processing
```python
from interview.weather import process_events

events = [
    {"type": "sample", "stationName": "Station A", "timestamp": 1000, "temperature": 25.0},
    {"type": "control", "command": "snapshot"}
]

for result in process_events(events):
    print(json.dumps(result))
```

### Multi-Station Aggregation
```python
events = [
    {"type": "sample", "stationName": "Station A", "timestamp": 1000, "temperature": 25.0},
    {"type": "sample", "stationName": "Station B", "timestamp": 1100, "temperature": 30.0},
    {"type": "sample", "stationName": "Station A", "timestamp": 1200, "temperature": 20.0},
    {"type": "control", "command": "snapshot"}
]
```

## Development Environment

### Setup
```bash
# Install dependencies
make deps

# Run tests
make test

# Continuous testing
make watch
```

### Code Quality
- **Type hints**: Full type annotation support
- **Documentation**: Comprehensive docstrings
- **Linting**: Pylint and MyPy integration
- **Testing**: Pytest with coverage reporting

## Performance Characteristics

### Memory Usage
- **O(k) memory**: Where k is the number of unique stations
- **Constant time**: O(1) operations for sample processing
- **Linear time**: O(n) for snapshot generation

### Scalability
- **Horizontal scaling**: Can handle multiple input streams
- **Vertical scaling**: Efficient single-threaded processing
- **State persistence**: Minimal memory footprint

## Error Scenarios

### Invalid Weather Samples
```python
# Missing required fields
{"type": "sample", "stationName": "Station A"}
# Raises: ValueError("Please verify input. Weather sample missing required fields.")
```

### Unknown Message Types
```python
# Unknown message type
{"type": "unknown", "data": "some data"}
# Raises: ValueError("Please verify input. Unknown message type.")
```

### Unknown Control Commands
```python
# Unknown control command
{"type": "control", "command": "unknown_command"}
# Raises: ValueError("Please verify input. Unknown control command.")
```

## Future Enhancements

### Potential Extensions
- **Additional metrics**: Humidity, wind speed, pressure
- **Time-based queries**: Historical data snapshots
- **Alerting system**: Threshold-based notifications
- **Data persistence**: Database integration
- **API endpoints**: RESTful service layer

### Scalability Improvements
- **Multi-threading**: Parallel processing capabilities
- **Distributed processing**: Cluster-based aggregation
- **Caching layer**: Redis integration for performance
- **Message queuing**: Kafka/RabbitMQ integration

## Best Practices Implemented

### Code Quality
- **Single responsibility**: Each function has a clear purpose
- **Error handling**: Comprehensive validation and error reporting
- **Documentation**: Clear docstrings and comments
- **Testing**: High test coverage with edge cases

### Performance
- **Memory efficiency**: Generator-based processing
- **Algorithm optimization**: Efficient data structures
- **Resource management**: Minimal memory footprint

### Maintainability
- **Modular design**: Easy to extend and modify
- **Clear interfaces**: Well-defined function signatures
- **Consistent patterns**: Uniform error handling and validation

## Conclusion

This weather data streaming processor demonstrates robust handling of real-time data aggregation with efficient memory usage and comprehensive error handling. The generator-based approach ensures scalability for large data streams while maintaining clean, maintainable code.

The implementation provides a solid foundation for weather data processing systems and can be easily extended for additional features and use cases. 
