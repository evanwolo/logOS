#!/usr/bin/env python3
"""
LogOS Alignment Verification

Verifies that the frozen alignment logic works correctly.
Tests all state transitions and exit codes.
"""

import sys
from logos.alignment import calculate_system_state


def test_case(name, daily_state, liturgical, unconfessed_count, expected_state):
    """Test a single scenario."""
    state = calculate_system_state(daily_state, liturgical, unconfessed_count)
    status = "✅" if state == expected_state else "❌"
    print(f"{status} {name}: {state} (expected {expected_state})")
    return state == expected_state


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("LOGOS ALIGNMENT VERIFICATION")
    print("=" * 70 + "\n")
    
    passed = 0
    total = 0
    
    # Test 1: STABLE - Perfect state
    print("[STABLE SCENARIOS]")
    total += 1
    if test_case(
        "Perfect practice",
        {"prayer_minutes": 120, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "STABLE"
    ):
        passed += 1
    
    total += 1
    if test_case(
        "STABLE with some screen time but good ratio",
        {"prayer_minutes": 100, "reading_minutes": 50, "screen_time_minutes": 300,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "STABLE"
    ):
        passed += 1
    
    total += 1
    if test_case(
        "STABLE with zero noise is perfect",
        {"prayer_minutes": 10, "reading_minutes": 5, "screen_time_minutes": 0,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "STABLE"
    ):
        passed += 1
    
    # Test 2: CRITICAL - Hamartia buffer overflow
    print("\n[CRITICAL - HAMARTIA BUFFER]")
    total += 1
    if test_case(
        "5 unconfessed sins → CRITICAL",
        {"prayer_minutes": 120, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        5,
        "CRITICAL"
    ):
        passed += 1
    
    total += 1
    if test_case(
        "10 unconfessed sins → CRITICAL",
        {"prayer_minutes": 120, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        10,
        "CRITICAL"
    ):
        passed += 1
    
    # Test 3: CRITICAL - Strict fast violation
    print("\n[CRITICAL - STRICT FAST VIOLATION]")
    total += 1
    if test_case(
        "Strict fast not observed → CRITICAL",
        {"prayer_minutes": 120, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": False, "prayed": True},
        {"fast_type": "strict", "feast": None, "feast_level": None},
        0,
        "CRITICAL"
    ):
        passed += 1
    
    # Test 4: CRITICAL - Prayer missed with sin
    print("\n[CRITICAL - PRAYER + SIN]")
    total += 1
    if test_case(
        "Prayer missed + 1 sin → CRITICAL",
        {"prayer_minutes": 0, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": False},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        1,
        "CRITICAL"
    ):
        passed += 1
    
    total += 1
    if test_case(
        "Prayer missed + 4 sins → CRITICAL",
        {"prayer_minutes": 0, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": False},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        4,
        "CRITICAL"
    ):
        passed += 1
    
    # Test 5: DEGRADED - Prayer missed alone
    print("\n[DEGRADED - PRAYER MISSED]")
    total += 1
    if test_case(
        "Prayer missed (no sin) → DEGRADED",
        {"prayer_minutes": 0, "reading_minutes": 45, "screen_time_minutes": 0,
         "fasted": True, "prayed": False},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "DEGRADED"
    ):
        passed += 1
    
    # Test 6: DEGRADED - Signal/noise ratio
    print("\n[DEGRADED - SIGNAL/NOISE RATIO]")
    total += 1
    if test_case(
        "Poor signal/noise ratio → DEGRADED",
        {"prayer_minutes": 10, "reading_minutes": 5, "screen_time_minutes": 300,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "DEGRADED"
    ):
        passed += 1
    
    total += 1
    if test_case(
        "Very poor ratio (0.05) → DEGRADED",
        {"prayer_minutes": 1, "reading_minutes": 1, "screen_time_minutes": 400,
         "fasted": True, "prayed": True},
        {"fast_type": "regular", "feast": None, "feast_level": None},
        0,
        "DEGRADED"
    ):
        passed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 70 + "\n")
    
    if passed == total:
        print("✅ All tests passed!")
        print("\nThe alignment logic is correctly frozen and working.")
        print("The state machine is deterministic and auditable.")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
