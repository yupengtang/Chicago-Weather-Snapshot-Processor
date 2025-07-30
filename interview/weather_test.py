import pytest
from . import weather


def test_weather_sample_processing():
    """Test processing of weather sample messages."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        }
    ]
    
    # Should not yield anything for sample only
    result = list(weather.process_events(events))
    assert result == []


def test_snapshot_with_single_station():
    """Test snapshot generation with single weather station."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1
    assert result[0]["type"] == "snapshot"
    assert result[0]["asOf"] == 1672531200000
    assert result[0]["stations"]["Foster Weather Station"]["high"] == 37.1
    assert result[0]["stations"]["Foster Weather Station"]["low"] == 37.1


def test_snapshot_with_multiple_stations():
    """Test snapshot generation with multiple weather stations."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "sample",
            "stationName": "Oak Street Weather Station",
            "timestamp": 1672531260000,
            "temperature": 42.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1
    snapshot = result[0]
    assert snapshot["type"] == "snapshot"
    assert snapshot["asOf"] == 1672531260000
    assert len(snapshot["stations"]) == 2
    assert snapshot["stations"]["Foster Weather Station"]["high"] == 37.1
    assert snapshot["stations"]["Foster Weather Station"]["low"] == 37.1
    assert snapshot["stations"]["Oak Street Weather Station"]["high"] == 42.5
    assert snapshot["stations"]["Oak Street Weather Station"]["low"] == 42.5


def test_snapshot_with_temperature_range():
    """Test snapshot with multiple temperature readings from same station."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531260000,
            "temperature": 42.5
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531320000,
            "temperature": 32.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1
    snapshot = result[0]
    assert snapshot["type"] == "snapshot"
    assert snapshot["asOf"] == 1672531320000
    assert snapshot["stations"]["Foster Weather Station"]["high"] == 42.5
    assert snapshot["stations"]["Foster Weather Station"]["low"] == 32.5


def test_reset_functionality():
    """Test reset control message functionality."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "reset"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1
    assert result[0]["type"] == "reset"
    assert result[0]["asOf"] == 1672531200000


def test_snapshot_after_reset():
    """Test that snapshot after reset returns no data."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "reset"
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1  # Only reset message, no snapshot
    assert result[0]["type"] == "reset"


def test_unknown_message_type():
    """Test handling of unknown message type."""
    events = [
        {
            "type": "unknown",
            "data": "some data"
        }
    ]
    
    with pytest.raises(ValueError, match="Please verify input. Unknown message type."):
        list(weather.process_events(events))


def test_unknown_control_command():
    """Test handling of unknown control command."""
    events = [
        {
            "type": "control",
            "command": "unknown_command"
        }
    ]
    
    with pytest.raises(ValueError, match="Please verify input. Unknown control command."):
        list(weather.process_events(events))


def test_invalid_sample_missing_fields():
    """Test handling of invalid sample with missing fields."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station"
            # Missing timestamp and temperature
        }
    ]
    
    with pytest.raises(ValueError, match="Please verify input. Weather sample missing required fields."):
        list(weather.process_events(events))


def test_snapshot_without_data():
    """Test snapshot command when no weather data is available."""
    events = [
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert result == []  # Should not yield anything


def test_reset_without_data():
    """Test reset command when no weather data is available."""
    events = [
        {
            "type": "control",
            "command": "reset"
        }
    ]
    
    result = list(weather.process_events(events))
    assert result == []  # Should not yield anything


def test_timestamp_ordering():
    """Test that latest timestamp is correctly tracked."""
    events = [
        {
            "type": "sample",
            "stationName": "Station A",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "sample",
            "stationName": "Station B",
            "timestamp": 1672531100000,  # Earlier timestamp
            "temperature": 42.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 1
    assert result[0]["asOf"] == 1672531200000  # Should use the latest timestamp


def test_multiple_snapshots():
    """Test multiple snapshot requests."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "snapshot"
        },
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531260000,
            "temperature": 42.5
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    result = list(weather.process_events(events))
    assert len(result) == 2
    
    # First snapshot
    assert result[0]["asOf"] == 1672531200000
    assert result[0]["stations"]["Foster Weather Station"]["high"] == 37.1
    assert result[0]["stations"]["Foster Weather Station"]["low"] == 37.1
    
    # Second snapshot
    assert result[1]["asOf"] == 1672531260000
    assert result[1]["stations"]["Foster Weather Station"]["high"] == 42.5
    assert result[1]["stations"]["Foster Weather Station"]["low"] == 37.1


def test_generator_behavior():
    """Test that the function behaves as a proper generator."""
    events = [
        {
            "type": "sample",
            "stationName": "Foster Weather Station",
            "timestamp": 1672531200000,
            "temperature": 37.1
        },
        {
            "type": "control",
            "command": "snapshot"
        }
    ]
    
    generator = weather.process_events(events)
    assert hasattr(generator, '__iter__')
    assert hasattr(generator, '__next__')
    
    result = list(generator)
    assert len(result) == 1
