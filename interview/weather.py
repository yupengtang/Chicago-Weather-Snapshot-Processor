from typing import Any, Iterable, Generator
from collections import defaultdict


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    """
    Process weather events and control messages.
    
    This generator function processes incoming weather samples and control messages,
    maintaining state of weather station data and producing appropriate output messages.
    
    Args:
        events: An iterable of dictionaries representing weather samples or control messages
        
    Yields:
        Dictionary objects representing output messages (snapshots, resets, etc.)
    """
    # Initialize state to track weather station data
    weather_data = defaultdict(lambda: {"high": float('-inf'), "low": float('inf')})
    latest_timestamp = None
    
    for event in events:
        event_type = event.get("type")
        
        if event_type == "sample":
            # Process weather sample
            station_name = event.get("stationName")
            timestamp = event.get("timestamp")
            temperature = event.get("temperature")
            
            # Validate required fields
            if station_name is None or timestamp is None or temperature is None:
                raise ValueError("Please verify input. Weather sample missing required fields.")
            
            # Update latest timestamp
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
            
            # Update station data
            station_data = weather_data[station_name]
            if temperature > station_data["high"]:
                station_data["high"] = temperature
            if temperature < station_data["low"]:
                station_data["low"] = temperature
                
        elif event_type == "control":
            # Process control message
            command = event.get("command")
            
            if command == "snapshot":
                # Generate snapshot if we have data
                if latest_timestamp is not None and weather_data:
                    snapshot = {
                        "type": "snapshot",
                        "asOf": latest_timestamp,
                        "stations": {}
                    }
                    
                    # Convert defaultdict to regular dict and handle infinite values
                    for station_name, data in weather_data.items():
                        if data["high"] != float('-inf') and data["low"] != float('inf'):
                            snapshot["stations"][station_name] = {
                                "high": data["high"],
                                "low": data["low"]
                            }
                    
                    # Only yield if we have valid station data
                    if snapshot["stations"]:
                        yield snapshot
                        
            elif command == "reset":
                # Reset all data
                weather_data.clear()
                if latest_timestamp is not None:
                    yield {
                        "type": "reset",
                        "asOf": latest_timestamp
                    }
                    
            else:
                # Unknown command
                raise ValueError("Please verify input. Unknown control command.")
                
        else:
            # Unknown message type
            raise ValueError("Please verify input. Unknown message type.")
