"""
LogOS Agenda CLI.
"""
import argparse
from logos.agenda import (
    commit, log_work, log_context_switch, 
    abandon_commitment, calculate_work_health
)
from logos.mutations import PASSIONS


def cmd_commit(args):
    """logos commit --deep "Description" --min 60"""
    wtype = 'deep' if args.deep else 'shallow'
    if args.admin:
        wtype = 'admin'
    
    cid = commit(args.description, wtype, args.minutes)
    print(f"Committed: [{wtype.upper()}] {args.description} ({args.minutes}m)")
    return 0


def cmd_work(args):
    """logos work --category deep_work_creative --minutes 45"""
    log_work(args.category, args.minutes, args.encroached)
    print(f"Logged: {args.minutes}m to {args.category}")
    return 0


def cmd_switch(args):
    """logos switch --from deep --to shallow --passion Acedia"""
    log_context_switch(args.from_type, args.to_type, args.passion, args.lag)
    print("Context switch recorded.")
    return 0


def cmd_abandon(args):
    """logos abandon --id 1 --passion Acedia"""
    abandon_commitment(args.id, args.passion)
    print(f"Commitment {args.id} abandoned due to {args.passion}.")
    return 0


def cmd_agenda_health(args):
    """logos agenda-health"""
    result = calculate_work_health()
    state = result['state']
    
    symbol = {
        "STABLE": "●",
        "DEGRADED": "◐",
        "CRITICAL": "✕",
    }.get(state, "?")
    
    print(f"{symbol} Work Health: {state}")
    if result['diagnosis'] != "Nominal":
        print(f"  Diagnosis: {result['diagnosis']}")
    
    # Exit code reflects state
    if state == "CRITICAL":
        return 2
    elif state == "DEGRADED":
        return 1
    return 0


# Integration helper
def register_agenda_commands(subparsers):
    """Register all Agenda Layer commands with the main parser."""
    
    # logos commit
    p_commit = subparsers.add_parser("commit", help="Log a work commitment")
    p_commit.add_argument("--description", required=True, help="Task description")
    p_commit.add_argument("--minutes", type=int, required=True, help="Committed duration in minutes")
    g = p_commit.add_mutually_exclusive_group(required=True)
    g.add_argument("--deep", action="store_true", help="Deep work commitment")
    g.add_argument("--shallow", action="store_true", help="Shallow work commitment")
    g.add_argument("--admin", action="store_true", help="Admin work commitment")
    p_commit.set_defaults(func=cmd_commit)

    # logos work
    p_work = subparsers.add_parser("work", help="Log completed work")
    p_work.add_argument("--category", required=True, choices=[
        'deep_work_creative', 'deep_work_analytical', 'deep_work_learning',
        'shallow_work_necessary', 'shallow_work_admin', 'shallow_work_waste'
    ], help="Work category")
    p_work.add_argument("--minutes", type=int, required=True, help="Minutes of work")
    p_work.add_argument("--encroached", action="store_true", help="Encroached on prayer time")
    p_work.set_defaults(func=cmd_work)

    # logos switch
    p_switch = subparsers.add_parser("switch", help="Log context switch")
    p_switch.add_argument("--from-type", dest="from_type", help="Previous work type")
    p_switch.add_argument("--to-type", dest="to_type", help="New work type")
    p_switch.add_argument("--passion", choices=PASSIONS, help="Passion that triggered switch")
    p_switch.add_argument("--lag", type=int, default=0, help="Resumption lag in minutes")
    p_switch.set_defaults(func=cmd_switch)

    # logos agenda-health
    p_health = subparsers.add_parser("agenda-health", help="Check work health")
    p_health.set_defaults(func=cmd_agenda_health)

    # logos abandon
    p_abandon = subparsers.add_parser("abandon", help="Abandon commitment")
    p_abandon.add_argument("--id", type=int, required=True, help="Commitment ID")
    p_abandon.add_argument("--passion", required=True, choices=PASSIONS, help="Passion that caused failure")
    p_abandon.set_defaults(func=cmd_abandon)
