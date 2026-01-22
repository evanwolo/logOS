"""
LogOS Command-Line Interface.

The CLI is the canonical interface.
No implicit state. No global configuration.
Every command reads truth from the database.
"""

import sys
import argparse
from datetime import datetime, date
from logos.alignment import calculate_system_state
from logos.db import fetch_system_health_today
from logos.mutations import (
    PASSIONS, log_hamartia, update_daily_state,
    fetch_unconfessed_sins, mark_confessed, fetch_today_state
)
from logos.cli_agenda import register_agenda_commands


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


def cmd_log_add(args):
    """
    log add — Append sin to hamartia_log (append-only).
    
    Requires explicit categorization of the passion.
    No edits. No deletes. Only confession can change state.
    """
    # Interactive mode: select passion
    if not args.passion:
        print("\nSelect Passion (Evagrius of Pontus):")
        for i, passion in enumerate(PASSIONS, 1):
            print(f"{i}. {passion}")
        
        try:
            choice = input("\n> ")
            passion_idx = int(choice) - 1
            if passion_idx < 0 or passion_idx >= len(PASSIONS):
                print("error: invalid selection", flush=True)
                return 1
            passion = PASSIONS[passion_idx]
        except (ValueError, KeyboardInterrupt):
            print("\nerror: cancelled", flush=True)
            return 1
    else:
        passion = args.passion
        if passion not in PASSIONS:
            print(f"error: passion must be one of: {', '.join(PASSIONS)}", flush=True)
            return 1
    
    # Get description
    if not args.description:
        try:
            description = input("\nEnter Description:\n> ")
            if not description.strip():
                print("error: description cannot be empty", flush=True)
                return 1
        except KeyboardInterrupt:
            print("\nerror: cancelled", flush=True)
            return 1
    else:
        description = args.description
    
    # Confirmation
    print(f"\nConfirm: [{passion}] \"{description}\"?", end=" ")
    try:
        confirm = input("(y/n) ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return 0
    except KeyboardInterrupt:
        print("\nerror: cancelled", flush=True)
        return 1
    
    # Log it (append-only)
    unconfessed_count = log_hamartia(passion, description)
    
    print(f"\nLogged. Unconfessed Count: {unconfessed_count}")
    print()
    
    return 0


def cmd_log_confess(args):
    """
    log confess — Mark sins as confessed (only state transition).
    
    This is the ONLY allowed state transition for hamartia_log.
    Requires explicit confirmation. Assumes sacramental confession.
    """
    sins = fetch_unconfessed_sins()
    
    if not sins:
        print("No unconfessed sins.")
        return 0
    
    print(f"\nUnconfessed Sins ({len(sins)}):")
    print("=" * 70)
    for sin in sins:
        print(f"  [{sin['id']}] {sin['date']} | {sin['passions']}")
        print(f"      {sin['description']}")
        print()
    
    print("=" * 70)
    print(f"\nMark {len(sins)} sin(s) as absolved?")
    print("This assumes sacramental confession has occurred.")
    
    try:
        confirm = input("\n(yes/no) ")
        if confirm.lower() != 'yes':
            print("Cancelled. No changes made.")
            return 0
    except KeyboardInterrupt:
        print("\nerror: cancelled", flush=True)
        return 1
    
    # Mark as confessed
    sin_ids = [sin['id'] for sin in sins]
    count = mark_confessed(sin_ids)
    
    print(f"\n✓ Marked {count} sin(s) as confessed.")
    print()
    
    return 0


def cmd_ascetic(args):
    """
    ascetic — Update daily_state (today only).
    
    Temporal constraint: Can only update TODAY.
    No retroactive changes allowed.
    """
    if args.subcommand == 'fast':
        update_daily_state(fasted=args.kept)
        status = "kept" if args.kept else "not kept"
        print(f"Fast: {status}")
    
    elif args.subcommand == 'pray':
        if args.done:
            update_daily_state(prayed=True)
            print("Prayer rule: completed")
        elif args.minutes:
            update_daily_state(prayer_minutes=args.minutes, prayed=True)
            print(f"Prayer: +{args.minutes} minutes")
    
    elif args.subcommand == 'read':
        update_daily_state(reading_minutes=args.minutes)
        print(f"Reading: +{args.minutes} minutes")
    
    elif args.subcommand == 'screen':
        update_daily_state(screen_time_minutes=args.minutes)
        print(f"Screen time: +{args.minutes} minutes")
    
    elif args.subcommand == 'status':
        state = fetch_today_state()
        if not state:
            print(f"No state recorded for {date.today()}")
            return 1
        
        print(f"\nDaily State ({date.today()}):")
        print("=" * 40)
        print(f"  Prayer: {state['prayer_minutes']} min")
        print(f" Reading: {state['reading_minutes']} min")
        print(f"  Screen: {state['screen_time_minutes']} min")
        print(f"  Fasted: {state['fasted']}")
        print(f"  Prayed: {state['prayed']}")
        print()
    
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
    
    # health command (Phase 3 - Read-only)
    parser_health = subparsers.add_parser(
        "health",
        help="Display system health status"
    )
    parser_health.set_defaults(func=cmd_health)
    
    # log command group (Phase 4 - Hamartia mutations)
    parser_log = subparsers.add_parser(
        "log",
        help="Manage hamartia log"
    )
    log_subparsers = parser_log.add_subparsers(dest="subcommand", help="Log commands")
    
    # log add
    parser_log_add = log_subparsers.add_parser(
        "add",
        help="Append sin to hamartia log (append-only)"
    )
    parser_log_add.add_argument("--passion", choices=PASSIONS, help="The passion")
    parser_log_add.add_argument("--description", help="Description of the sin")
    parser_log_add.set_defaults(func=cmd_log_add)
    
    # log confess
    parser_log_confess = log_subparsers.add_parser(
        "confess",
        help="Mark all sins as confessed (only state transition)"
    )
    parser_log_confess.set_defaults(func=cmd_log_confess)
    
    # ascetic command group (Phase 4 - Daily state mutations)
    parser_ascetic = subparsers.add_parser(
        "ascetic",
        help="Update daily ascetic practice (today only)"
    )
    ascetic_subparsers = parser_ascetic.add_subparsers(dest="subcommand", help="Ascetic commands")
    
    # ascetic fast
    parser_fast = ascetic_subparsers.add_parser(
        "fast",
        help="Set fasting status for today"
    )
    parser_fast.add_argument("--kept", action="store_true", help="Fast was kept")
    parser_fast.set_defaults(func=cmd_ascetic)
    
    # ascetic pray
    parser_pray = ascetic_subparsers.add_parser(
        "pray",
        help="Log prayer for today"
    )
    parser_pray.add_argument("--minutes", type=int, help="Minutes of prayer")
    parser_pray.add_argument("--done", action="store_true", help="Mark prayer rule complete")
    parser_pray.set_defaults(func=cmd_ascetic)
    
    # ascetic read
    parser_read = ascetic_subparsers.add_parser(
        "read",
        help="Log reading for today"
    )
    parser_read.add_argument("--minutes", type=int, required=True, help="Minutes of reading")
    parser_read.set_defaults(func=cmd_ascetic)
    
    # ascetic screen
    parser_screen = ascetic_subparsers.add_parser(
        "screen",
        help="Log screen time for today"
    )
    parser_screen.add_argument("--minutes", type=int, required=True, help="Minutes of screen time")
    parser_screen.set_defaults(func=cmd_ascetic)
    
    # ascetic status
    parser_status = ascetic_subparsers.add_parser(
        "status",
        help="Show today's ascetic practice"
    )
    parser_status.set_defaults(func=cmd_ascetic)
    
    # Register Agenda Layer commands
    register_agenda_commands(subparsers)
    
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
