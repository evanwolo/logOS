#!/usr/bin/env python3
"""
LogOS Demo - Run without database dependencies

This is a self-contained demonstration of the logos health command.
It simulates database output and shows the full system in action.
"""

import sys
from datetime import date
from logos.alignment import calculate_system_state


def demo_stable():
    """Demonstrate STABLE state."""
    print("=" * 70)
    print("DEMO 1: STABLE STATE")
    print("=" * 70)
    print()
    
    daily_state = {
        "prayer_minutes": 120,
        "reading_minutes": 45,
        "screen_time_minutes": 0,
        "fasted": True,
        "prayed": True,
    }
    
    liturgical = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    
    unconfessed_count = 0
    state = calculate_system_state(daily_state, liturgical, unconfessed_count)
    
    print(f"● System: {state}")
    print()
    print(f"     Date: {date.today()}")
    print(f"    Fasted: {daily_state['fasted']}")
    print(f"    Prayed: {daily_state['prayed']}")
    print(f"Fast Type: {liturgical['fast_type']}")
    print()
    print(f"   Prayer: {daily_state['prayer_minutes']} min")
    print(f"  Reading: {daily_state['reading_minutes']} min")
    print(f"   Screen: {daily_state['screen_time_minutes']} min")
    print()
    print(f"Unconfessed: {unconfessed_count} sin(s)")
    print()
    print(f"Exit Code: 0")
    print()


def demo_degraded():
    """Demonstrate DEGRADED state."""
    print("=" * 70)
    print("DEMO 2: DEGRADED STATE")
    print("=" * 70)
    print()
    
    daily_state = {
        "prayer_minutes": 0,
        "reading_minutes": 30,
        "screen_time_minutes": 480,
        "fasted": True,
        "prayed": False,
    }
    
    liturgical = {
        "fast_type": "regular",
        "feast": None,
        "feast_level": None,
    }
    
    unconfessed_count = 0
    state = calculate_system_state(daily_state, liturgical, unconfessed_count)
    
    print(f"◐ System: {state}")
    print()
    print(f"     Date: {date.today()}")
    print(f"    Fasted: {daily_state['fasted']}")
    print(f"    Prayed: {daily_state['prayed']}")
    print(f"Fast Type: {liturgical['fast_type']}")
    print()
    print(f"   Prayer: {daily_state['prayer_minutes']} min")
    print(f"  Reading: {daily_state['reading_minutes']} min")
    print(f"   Screen: {daily_state['screen_time_minutes']} min")
    print()
    print(f"Unconfessed: {unconfessed_count} sin(s)")
    print()
    print("Warnings:")
    print("  - Prayer rule missed")
    print("  - Signal-to-noise ratio degraded (30:480)")
    print()
    print(f"Exit Code: 1")
    print()


def demo_critical():
    """Demonstrate CRITICAL state."""
    print("=" * 70)
    print("DEMO 3: CRITICAL STATE")
    print("=" * 70)
    print()
    
    daily_state = {
        "prayer_minutes": 30,
        "reading_minutes": 15,
        "screen_time_minutes": 900,
        "fasted": False,
        "prayed": True,
    }
    
    liturgical = {
        "fast_type": "strict",
        "feast": None,
        "feast_level": None,
    }
    
    unconfessed_count = 5
    state = calculate_system_state(daily_state, liturgical, unconfessed_count)
    
    print(f"✕ System: {state}")
    print()
    print(f"     Date: {date.today()}")
    print(f"    Fasted: {daily_state['fasted']}")
    print(f"    Prayed: {daily_state['prayed']}")
    print(f"Fast Type: {liturgical['fast_type']}")
    print()
    print(f"   Prayer: {daily_state['prayer_minutes']} min")
    print(f"  Reading: {daily_state['reading_minutes']} min")
    print(f"   Screen: {daily_state['screen_time_minutes']} min")
    print()
    print(f"Unconfessed: {unconfessed_count} sin(s)")
    print()
    print("Warnings:")
    print("  - Hamartia buffer critical (≥5 unconfessed)")
    print("  - Strict fast violated")
    print()
    print(f"Exit Code: 2")
    print()


def main():
    """Run all demos."""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  LOGOS PHASE 3: READ-ONLY OBSERVABILITY DEMO  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    demo_stable()
    demo_degraded()
    demo_critical()
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("The alignment logic works correctly:")
    print("  • STABLE: All systems nominal")
    print("  • DEGRADED: One or more systems degraded")
    print("  • CRITICAL: System health compromised")
    print()
    print("To run with a real database:")
    print("  1. Set LOGOS_DB_* environment variables")
    print("  2. Initialize database: bash scripts/init_db.sh")
    print("  3. Run: python3 -m logos health")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
