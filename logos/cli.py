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
    PASSIONS, log_hamartia, update_daily_state,
    fetch_unconfessed_sins, fetch_today_state,
    record_sacrament, complete_penance, FAST_BREAK_REASONS
from logos.cli_agenda import register_agenda_commands


def format_health_output(diagnostic, health_data):
    """
    Format system health output in systemctl style.
    
    Args:
        diagnostic: dict with keys "state", "diagnosis", "counsel"
        health_data: dict with health information
        
    Returns:
        str: Formatted output
    """
    lines = []
    
    state = diagnostic["state"]
    diagnosis = diagnostic["diagnosis"]
    counsel = diagnostic["counsel"]
    
    # Status line
    status_symbol = {
        "STABLE": "●",
        "DEGRADED": "◐",
        "CRITICAL": "✕",
    }.get(state, "?")
    
    lines.append(f"{status_symbol} System: {state} [{diagnosis}]")
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
    
    # Counsel
    lines.append("")
    lines.append(f"Counsel: {counsel}")
    
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
        
        # Signal/Noise provided by alignment engine
        metrics = diagnostic.get("metrics")
        if metrics:
             ratio = metrics.get("ratio")
             if ratio is not None and ratio < 0.1:
                 noise = metrics.get("noise", 0)
                 signal = metrics.get("signal", 0)
                 lines.append(f"  - Signal-to-noise ratio degraded ({signal:.0f}:{noise})")

        # Pattern Analysis (Phase 6)
        if health_data["unconfessed_count"] > 0:
            try:
                from logos.patterns import analyze_hamartia_patterns
                conn = get_connection()
                patterns = analyze_hamartia_patterns(conn)
                conn.close() # optimize later
                
                lines.append("")
                lines.append("Pattern Analysis:")
                if patterns["dominant_passion"]:
                    lines.append(f"  Dominant: {patterns['dominant_passion']} ({patterns['dominant_count']} occurrences)")
                if patterns["peak_time"]:
                    lines.append(f"  Peak Time: {patterns['peak_time']}")
                if patterns["causal_chain"]:
                    lines.append(f"  Chain: {patterns['causal_chain']}")
                if patterns["screen_correlation"]:
                    lines.append(f"  ! High screen entertainment correlates with sin")
            except Exception:
                pass # Fail silently on pattern error to preserve core health output
    
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
        # Phase 4 Granular Fields
        "prayer_interruptions": health_data.get("prayer_interruptions", 0),
        "fast_break_reason": health_data.get("fast_break_reason"),
        "screen_time_work": health_data.get("screen_time_work", 0),
        "screen_time_social": health_data.get("screen_time_social", 0),
        "screen_time_entertainment": health_data.get("screen_time_entertainment", 0),
        "screen_time_edifying": health_data.get("screen_time_edifying", 0),
    }
    
    liturgical_context = {
        "fast_type": health_data["fast_type"],
        "feast": health_data["feast"],
        "feast_level": health_data["feast_level"],
    }
    
    unconfessed_count = health_data["unconfessed_count"]
    
    # Evaluate system state
    diagnostic = calculate_system_state(daily_state, liturgical_context, unconfessed_count)
    
    # Output result
    output = format_health_output(diagnostic, health_data)
    print(output)
    
    # Exit code reflects state
    state = diagnostic["state"]
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
    log confess — Record the Sacrament of Confession.
    
    ORTHODOX CORRECTION (Heresy II): Confession is not a toggle.
    This records the sacramental EVENT, then links absolution to it.
    
    "Whose sins you forgive are forgiven them." (John 20:23)
    """
    sins = fetch_unconfessed_sins()
    
    if not sins:
        print("No unconfessed sins. Glory to God.")
        return 0
    
    print(f"\nUnconfessed Sins ({len(sins)}):")
    print("=" * 70)
    for sin in sins:
        print(f"  [{sin['id']}] {sin['date']} | {sin['passions']}")
        print(f"      {sin['description']}")
        print()
    
    print("=" * 70)
    print("\n── THE SACRAMENT ──")
    print("Confession is not a database toggle. It is an encounter with Grace.")
    print()
    
    try:
        # Collect sacramental context
        if hasattr(args, 'father') and args.father:
            spiritual_father = args.father
        else:
            spiritual_father = input("Spiritual Father's name: ").strip()
            if not spiritual_father:
                print("error: Confession requires priesthood. Cannot proceed without spiritual father.")
                return 1
        
        if hasattr(args, 'penance') and args.penance:
            penance = args.penance
        else:
            penance = input("Penance assigned: ").strip()
            if not penance:
                print("error: Confession without epitimia is incomplete.")
                return 1
        
        notes = input("Notes (or press Enter to skip): ").strip() or None
        
        print(f"\nRecord absolution of {len(sins)} sin(s) by Fr. {spiritual_father}?")
        print(f"Penance: {penance}")
        confirm = input("(yes/no) ")
        if confirm.lower() != 'yes':
            print("Cancelled. No changes made.")
            return 0
            
    except KeyboardInterrupt:
        print("\nerror: cancelled", flush=True)
        return 1
    
    # Record the Sacrament
    sin_ids = [sin['id'] for sin in sins]
    result = record_sacrament(spiritual_father, penance, notes, sin_ids)
    
    print(f"\n✓ Sacrament recorded (ID: {result['confession_id']})")
    print(f"✓ {result['count_absolved']} sin(s) absolved.")
    if penance:
        print(f"  Penance: {penance}")
    print("\nGo in peace. Sin no more. (John 8:11)")
    print()
    
    return 0


def cmd_ascetic(args):
    """
    ascetic — Update daily_state (today only).
    
    ORTHODOX CORRECTION (Heresy I): Now accepts Phase 4 granular fields
    that alignment.py expects for proper diagnosis.
    
    Temporal constraint: Can only update TODAY.
    No retroactive changes allowed. No negative values (Heresy IV).
    """
    try:
        if args.subcommand == 'fast':
            reason = getattr(args, 'reason', None)
            if args.kept:
                update_daily_state(fasted=True)
                print("Fast: kept")
            else:
                if not reason:
                    print("Why was the fast broken? (temptation/necessity/charity/ignorance)")
                    reason = input("> ").strip()
                if reason not in FAST_BREAK_REASONS:
                    print(f"error: reason must be one of: {', '.join(FAST_BREAK_REASONS)}")
                    return 1
                update_daily_state(fasted=False, fast_break_reason=reason)
                print(f"Fast: broken ({reason})")
        
        elif args.subcommand == 'pray':
            interruptions = getattr(args, 'interruptions', None)
            if args.done:
                update_daily_state(prayed=True, prayer_interruptions=interruptions)
                msg = "Prayer rule: completed"
                if interruptions:
                    msg += f" ({interruptions} interruptions)"
                print(msg)
            elif args.minutes:
                update_daily_state(prayer_minutes=args.minutes, prayed=True, prayer_interruptions=interruptions)
                msg = f"Prayer: +{args.minutes} minutes"
                if interruptions:
                    msg += f" ({interruptions} interruptions)"
                print(msg)
        
        elif args.subcommand == 'read':
            update_daily_state(reading_minutes=args.minutes)
            print(f"Reading: +{args.minutes} minutes")
        
        elif args.subcommand == 'screen':
            # Phase 4: Granular screen time categories
            category = getattr(args, 'category', None)
            minutes = args.minutes
            
            if category == 'work':
                update_daily_state(screen_time_work=minutes)
                print(f"Screen (work): +{minutes} minutes")
            elif category == 'social':
                update_daily_state(screen_time_social=minutes)
                print(f"Screen (social - noise): +{minutes} minutes")
            elif category == 'entertainment':
                update_daily_state(screen_time_entertainment=minutes)
                print(f"Screen (entertainment - noise): +{minutes} minutes")
            elif category == 'edifying':
                update_daily_state(screen_time_edifying=minutes)
                print(f"Screen (edifying - signal): +{minutes} minutes")
            else:
                # Legacy: total screen time
                update_daily_state(screen_time_minutes=minutes)
                print(f"Screen time: +{minutes} minutes (use --category for Signal/Noise tracking)")
        
        elif args.subcommand == 'status':
            state = fetch_today_state()
            if not state:
                print(f"No state recorded for {date.today()}")
                return 1
            
            print(f"\nDaily State ({date.today()}):")
            print("=" * 50)
            print(f"       Prayer: {state['prayer_minutes']} min")
            if state.get('prayer_interruptions'):
                print(f" Interruptions: {state['prayer_interruptions']}")
            print(f"      Reading: {state['reading_minutes']} min")
            print(f"       Fasted: {state['fasted']}")
            if state.get('fast_break_reason'):
                print(f"  Break Reason: {state['fast_break_reason']}")
            print(f"       Prayed: {state['prayed']}")
            print()
            print("Screen Time (Signal/Noise):")
            print(f"         Work: {state.get('screen_time_work', 0)} min (neutral)")
            print(f"     Edifying: {state.get('screen_time_edifying', 0)} min (signal)")
            print(f"       Social: {state.get('screen_time_social', 0)} min (noise)")
            print(f"Entertainment: {state.get('screen_time_entertainment', 0)} min (noise)")
            if state.get('screen_time_minutes'):
                print(f"  Legacy Total: {state['screen_time_minutes']} min")
            print()
        
        return 0
        
    except ValueError as e:
        print(f"error: {e}", flush=True)
        return 1


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
        help="Record the Sacrament of Confession"
    )
    parser_log_confess.add_argument("--father", help="Name of Spiritual Father")
    parser_log_confess.add_argument("--penance", help="Penance assigned")
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
    parser_fast.add_argument("--reason", choices=FAST_BREAK_REASONS, help="Why fast was broken")
    parser_fast.set_defaults(func=cmd_ascetic)

    # penance command
    parser_penance = subparsers.add_parser(
        "penance", 
        help="Complete assigned penance"
    )
    parser_penance.add_argument("confession_id", type=int, help="Confession ID")
    parser_penance.set_defaults(func=cmd_complete_penance)
    
    # ascetic pray
    parser_pray = ascetic_subparsers.add_parser(
        "pray",
        help="Log prayer for today"
    )
    parser_pray.add_argument("--minutes", type=int, help="Minutes of prayer")
    parser_pray.add_argument("--done", action="store_true", help="Mark prayer rule complete")
    parser_pray.add_argument("--interruptions", type=int, help="Number of times attention wandered")
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
        help="Log screen time for today (use --category for Signal/Noise tracking)"
    )
    parser_screen.add_argument("--minutes", type=int, required=True, help="Minutes of screen time")
    parser_screen.add_argument("--category", choices=['work', 'social', 'entertainment', 'edifying'],
        help="Screen time category: work (neutral), social/entertainment (noise), edifying (signal)")
    parser_screen.set_defaults(func=cmd_ascetic)
    
    # ascetic status
    parser_status = ascetic_subparsers.add_parser(
        "status",
        help="Show today's ascetic practice"
    )
    parser_status.set_defaults(func=cmd_ascetic)
    
    # export command (Phase 7 - Collapse Resilience)
    parser_export = subparsers.add_parser(
        "export",
        help="Export spiritual log to plaintext"
    )
    parser_export.add_argument("--file", default="spiritual-log.txt", help="Output filename")
    parser_export.set_defaults(func=lambda args: __import__('logos.export').export.export_to_plaintext(args.file))

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
