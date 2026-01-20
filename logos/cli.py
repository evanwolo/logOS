"""
LogOS Command-Line Interface.

The CLI is the canonical interface.
No implicit state. No global configuration.
Every command reads truth from the database.
"""

import sys
import argparse
from datetime import datetime
from logos.alignment import calculate_system_state
from logos.db import fetch_system_health_today


def format_health_output(state, health_data):
    """
    Format system health output in systemctl style.
    
    Args:
        state: str ("STABLE", "DEGRADED", or "CRITICAL")
        health_data: dict with health information
        
    Returns:
        str: Formatted output
    """
    lines = []
    
    # Status line
    status_symbol = {
        "STABLE": "●",
        "DEGRADED": "◐",
        "CRITICAL": "✕",
    }.get(state, "?")
    
    lines.append(f"{status_symbol} System: {state}")
    lines.append("")
    
    # Health details
    lines.append(f"     Date: {health_data['date']}")
    lines.append(f"    Fasted: {health_data['fasted']}")
    lines.append(f"    Prayed: {health_data['prayed']}")
    
    if health_data["fast_type"]:
        lines.append(f"Fast Type: {health_data['fast_type']}")
    
    if health_data["feast"]:
        lines.append(f"    Feast: {health_data['feast']}")
    
    lines.append("")
    lines.append(f"   Prayer: {health_data['prayer_minutes']} min")
    lines.append(f"  Reading: {health_data['reading_minutes']} min")
    lines.append(f"   Screen: {health_data['screen_time_minutes']} min")
    
    lines.append("")
    lines.append(f"Unconfessed: {health_data['unconfessed_count']} sin(s)")
    
    # Warnings for non-stable states
    if state != "STABLE":
        lines.append("")
        lines.append("Warnings:")
        
        if health_data["unconfessed_count"] >= 5:
            lines.append(f"  - Hamartia buffer critical (≥5 unconfessed)")
        
        if health_data["fast_type"] == "strict" and not health_data["fasted"]:
            lines.append(f"  - Strict fast violated")
        
        if not health_data["prayed"]:
            if health_data["unconfessed_count"] > 0:
                lines.append(f"  - Prayer missed with unconfessed sin")
            else:
                lines.append(f"  - Prayer rule missed")
        
        noise = health_data["screen_time_minutes"]
        signal = health_data["prayer_minutes"] + health_data["reading_minutes"]
        if noise > 0 and signal / noise < 0.1:
            lines.append(f"  - Signal-to-noise ratio degraded ({signal:.0f}:{noise})")
    
    return "\n".join(lines)


def cmd_health(args):
    """
    health — Display system health status.
    
    Reads from database, applies alignment logic, outputs state.
    No mutation. No caching. Always true.
    """
    health_data = fetch_system_health_today()
    
    # Prepare arguments for alignment function
    daily_state = {
        "prayer_minutes": health_data["prayer_minutes"],
        "reading_minutes": health_data["reading_minutes"],
        "screen_time_minutes": health_data["screen_time_minutes"],
        "fasted": health_data["fasted"],
        "prayed": health_data["prayed"],
    }
    
    liturgical_context = {
        "fast_type": health_data["fast_type"],
        "feast": health_data["feast"],
        "feast_level": health_data["feast_level"],
    }
    
    unconfessed_count = health_data["unconfessed_count"]
    
    # Evaluate system state
    state = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    
    # Output result
    output = format_health_output(state, health_data)
    print(output)
    
    # Exit code reflects state
    if state == "CRITICAL":
        return 2
    elif state == "DEGRADED":
        return 1
    else:
        return 0


def main():
    """
    LogOS command-line interface.
    
    Entry point. No global state. All commands are independent.
    """
    parser = argparse.ArgumentParser(
        prog="logos",
        description="LogOS — Metaphysical truth engine",
        add_help=True,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # health command
    parser_health = subparsers.add_parser(
        "health",
        help="Display system health status"
    )
    parser_health.set_defaults(func=cmd_health)
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command, print help
    if args.command is None:
        parser.print_help()
        return 0
    
    # Execute command
    try:
        exit_code = args.func(args)
        return exit_code if exit_code is not None else 0
    except Exception as e:
        print(f"error: {e}", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
