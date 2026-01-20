#!/usr/bin/env python3
"""
LogOS health command tests.

Tests the end-to-end pipeline:
1. Fetch system health data
2. Call alignment logic
3. Format output
4. Verify exit codes

Usage: python -m tests.test_health
"""

import sys
import os
from unittest.mock import patch
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logos.cli import cmd_health, format_health_output
from logos.alignment import calculate_system_state


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: expected {expected}, got {actual}")
            print(f"  ✗ {test_name}")
    
    def assert_in(self, substring, text, test_name):
        if substring in text:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: '{substring}' not in output")
            print(f"  ✗ {test_name}")
    
    def report(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Tests: {total} | Passed: {self.passed} | Failed: {self.failed}")
        if self.errors:
            print(f"\nFailures:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")
        return self.failed == 0


def test_health_output_formatting():
    print("\n[Alignment & Output Formatting]")
    results = TestResults()
    
    # Test STABLE output
    health_data = {
        "date": date(2026, 1, 20),
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": False,
        "prayed": True,
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
        "unconfessed_count": 0,
    }
    
    output = format_health_output("STABLE", health_data)
    results.assert_in("● System: STABLE", output, "STABLE state symbol")
    results.assert_in("Prayer: 120 min", output, "Prayer minutes displayed")
    results.assert_in("Screen: 0 min", output, "Screen time displayed")
    results.assert_in("Warnings:", output, "No warnings for STABLE", negate=True)
    
    # Test DEGRADED output
    health_data["prayed"] = False
    output = format_health_output("DEGRADED", health_data)
    results.assert_in("◐ System: DEGRADED", output, "DEGRADED state symbol")
    results.assert_in("Warnings:", output, "Warnings shown for DEGRADED")
    
    # Test CRITICAL output
    health_data["unconfessed_count"] = 5
    output = format_health_output("CRITICAL", health_data)
    results.assert_in("✕ System: CRITICAL", output, "CRITICAL state symbol")
    results.assert_in("Hamartia buffer critical", output, "Hamartia warning shown")
    
    return results


def test_alignment_logic():
    print("\n[Alignment Function Logic]")
    results = TestResults()
    
    # Test 1: STABLE state
    daily_state = {
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": True,
        "prayed": True,
    }
    liturgical = {"fast_type": "regular", "feast": None, "feast_level": None}
    state = calculate_system_state(daily_state, liturgical, 0)
    results.assert_equal(state, "STABLE", "STABLE with perfect state")
    
    # Test 2: CRITICAL - hamartia buffer
    state = calculate_system_state(daily_state, liturgical, 5)
    results.assert_equal(state, "CRITICAL", "CRITICAL with 5+ unconfessed sins")
    
    # Test 3: CRITICAL - strict fast violation
    daily_state["fasted"] = False
    state = calculate_system_state(daily_state, {"fast_type": "strict", "feast": None, "feast_level": None}, 0)
    results.assert_equal(state, "CRITICAL", "CRITICAL with strict fast violation")
    
    # Test 4: CRITICAL - missed prayer with sin
    daily_state["fasted"] = True
    daily_state["prayed"] = False
    state = calculate_system_state(daily_state, liturgical, 2)
    results.assert_equal(state, "CRITICAL", "CRITICAL with missed prayer and sin")
    
    # Test 5: DEGRADED - missed prayer alone
    state = calculate_system_state(daily_state, liturgical, 0)
    results.assert_equal(state, "DEGRADED", "DEGRADED with missed prayer")
    
    # Test 6: DEGRADED - bad signal-to-noise ratio
    daily_state["prayed"] = True
    daily_state["prayer_minutes"] = 10
    daily_state["reading_minutes"] = 5
    daily_state["screen_time_minutes"] = 600
    state = calculate_system_state(daily_state, liturgical, 0)
    results.assert_equal(state, "DEGRADED", "DEGRADED with poor signal-to-noise ratio")
    
    # Test 7: STABLE - zero noise is perfect
    daily_state["screen_time_minutes"] = 0
    state = calculate_system_state(daily_state, liturgical, 0)
    results.assert_equal(state, "STABLE", "STABLE with zero screen time")
    
    return results


def test_exit_codes():
    print("\n[Exit Codes]")
    results = TestResults()
    
    with patch("logos.cli.fetch_system_health_today") as mock_fetch:
        # Test STABLE exit code
        mock_fetch.return_value = {
            "date": date(2026, 1, 20),
            "prayer_minutes": 120,
            "reading_minutes": 45,
            "screen_time_minutes": 0,
            "fasted": True,
            "prayed": True,
            "fast_type": "regular",
            "feast": None,
            "feast_level": None,
            "unconfessed_count": 0,
        }
        exit_code = cmd_health(None)
        results.assert_equal(exit_code, 0, "Exit code 0 for STABLE")
        
        # Test DEGRADED exit code
        mock_fetch.return_value["prayed"] = False
        exit_code = cmd_health(None)
        results.assert_equal(exit_code, 1, "Exit code 1 for DEGRADED")
        
        # Test CRITICAL exit code
        mock_fetch.return_value["unconfessed_count"] = 5
        exit_code = cmd_health(None)
        results.assert_equal(exit_code, 2, "Exit code 2 for CRITICAL")
    
    return results


def main():
    print("="*60)
    print("LogOS: health command tests")
    print("="*60)
    
    all_results = []
    all_results.append(test_alignment_logic())
    all_results.append(test_health_output_formatting())
    all_results.append(test_exit_codes())
    
    print("\n" + "="*60)
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total = total_passed + total_failed
    
    print(f"TOTAL: {total} tests | {total_passed} passed | {total_failed} failed")
    
    if total_failed == 0:
        print("\n✓ All tests passed!")
        print("="*60 + "\n")
        return 0
    else:
        print(f"\n✗ {total_failed} test(s) failed")
        print("="*60 + "\n")
        return 1


# Patch the assert_in method to handle negation
TestResults.assert_in_original = TestResults.assert_in
def assert_in_with_negate(self, substring, text, test_name, negate=False):
    if negate:
        if substring not in text:
            self.passed += 1
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: '{substring}' found in output (should not be)")
            print(f"  ✗ {test_name}")
    else:
        self.assert_in_original(substring, text, test_name)

TestResults.assert_in = assert_in_with_negate


if __name__ == "__main__":
    sys.exit(main())
