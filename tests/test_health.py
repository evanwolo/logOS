#!/usr/bin/env python3
"""
Integration test for logos health command.

This tests the end-to-end pipeline:
1. Fetch system health data
2. Call alignment logic
3. Format output
4. Verify exit codes

Run with: python -m pytest tests/test_health.py
"""

import sys
import os
from unittest.mock import patch, MagicMock
from datetime import date

# Add logos to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logos.cli import cmd_health, format_health_output
from logos.alignment import calculate_system_state


def test_health_output_stable():
    """Test health output formatting for STABLE state."""
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
    assert "● System: STABLE" in output
    assert "Prayer: 120 min" in output
    assert "Screen: 0 min" in output
    assert "Warnings:" not in output
    print("✓ test_health_output_stable passed")


def test_health_output_degraded():
    """Test health output formatting for DEGRADED state."""
    health_data = {
        "date": date(2026, 1, 20),
        "prayer_minutes": 10,
        "reading_minutes": 5,
        "screen_time_minutes": 600,
        "fasted": False,
        "prayed": False,
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
        "unconfessed_count": 0,
    }
    
    output = format_health_output("DEGRADED", health_data)
    assert "◐ System: DEGRADED" in output
    assert "Warnings:" in output
    print("✓ test_health_output_degraded passed")


def test_health_output_critical():
    """Test health output formatting for CRITICAL state."""
    health_data = {
        "date": date(2026, 1, 20),
        "prayer_minutes": 0,
        "reading_minutes": 0,
        "screen_time_minutes": 1000,
        "fasted": False,
        "prayed": False,
        "fast_type": "strict",
        "feast": None,
        "feast_level": None,
        "unconfessed_count": 5,
    }
    
    output = format_health_output("CRITICAL", health_data)
    assert "✕ System: CRITICAL" in output
    assert "Warnings:" in output
    assert "Hamartia buffer critical" in output
    print("✓ test_health_output_critical passed")


def test_alignment_stable():
    """Test alignment function returns STABLE correctly."""
    daily_state = {
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": True,
        "prayed": True,
    }
    liturgical_context = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    unconfessed_count = 0
    
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    assert state == "STABLE"
    print("✓ test_alignment_stable passed")


def test_alignment_critical_hamartia():
    """Test alignment function detects hamartia buffer overflow."""
    daily_state = {
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": True,
        "prayed": True,
    }
    liturgical_context = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    unconfessed_count = 5
    
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    assert state == "CRITICAL"
    print("✓ test_alignment_critical_hamartia passed")


def test_alignment_critical_strict_fast():
    """Test alignment function detects strict fast violations."""
    daily_state = {
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": False,  # Violated!
        "prayed": True,
    }
    liturgical_context = {
        "fast_type": "strict",
        "feast": None,
        "feast_level": None,
    }
    unconfessed_count = 0
    
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    assert state == "CRITICAL"
    print("✓ test_alignment_critical_strict_fast passed")


def test_alignment_degraded_no_prayer():
    """Test alignment function detects missed prayer."""
    daily_state = {
        "prayer_minutes": 0,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": True,
        "prayed": False,  # Missed!
    }
    liturgical_context = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    unconfessed_count = 0
    
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    assert state == "DEGRADED"
    print("✓ test_alignment_degraded_no_prayer passed")


def test_alignment_degraded_signal_noise():
    """Test alignment function detects signal-to-noise degradation."""
    daily_state = {
        "prayer_minutes": 10,
        "reading_minutes": 5,
        "screen_time_minutes": 600,  # High noise
        "fasted": True,
        "prayed": True,
    }
    liturgical_context = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    unconfessed_count = 0
    
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    assert state == "DEGRADED"
    print("✓ test_alignment_degraded_signal_noise passed")


def test_cmd_health_with_mock():
    """Test cmd_health function with mocked database."""
    with patch("logos.cli.fetch_system_health_today") as mock_fetch:
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
        assert exit_code == 0  # STABLE
        print("✓ test_cmd_health_with_mock passed")


if __name__ == "__main__":
    test_health_output_stable()
    test_health_output_degraded()
    test_health_output_critical()
    test_alignment_stable()
    test_alignment_critical_hamartia()
    test_alignment_critical_strict_fast()
    test_alignment_degraded_no_prayer()
    test_alignment_degraded_signal_noise()
    test_cmd_health_with_mock()
    
    print("\n✓ All tests passed")
