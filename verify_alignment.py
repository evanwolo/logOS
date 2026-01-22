
import sys
from logos.alignment import calculate_system_state

def test_alignment():
    # Test case: Valid Signal/Noise
    state = {
        "prayer_minutes": 30,
        "reading_minutes": 15,
        "screen_time_edifying": 15, # Signal = 60
        "screen_time_social": 300,  # Noise = 600
        "screen_time_entertainment": 300,
        "fasted": True,
        "prayed": True
    }
    
    context = {
        "fast_type": "regular",
        "feast": None
    }
    
    result = calculate_system_state(state, context, unconfessed_count=0)
    print(f"Result: {result}")
    
    if "signal_to_noise_ratio" not in result:
        print("FAIL: signal_to_noise_ratio missing")
        return False
        
    if result["state"] != "DEGRADED":
        print(f"FAIL: Expected DEGRADED, got {result['state']}")
        return False
        
    return True

if __name__ == "__main__":
    if test_alignment():
        print("Alignment Test PASSED")
    else:
        print("Alignment Test FAILED")
        sys.exit(1)
