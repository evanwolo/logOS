"""
LogOS Alignment Module

This module contains the authoritative system state calculation logic.
The function and evaluation order are frozen by design.
"""


def calculate_system_state(daily_state, liturgical_context, unconfessed_count):
    """
    LogOS Alignment Function — AUTHORITATIVE SPEC

    This function evaluates system health using a STATE MACHINE, not a score.

    DO NOT:
    - Convert this logic into percentages, points, or normalized values
    - Introduce decay, time-weighting, or forgiveness over time
    - Allow positive behavior to offset unresolved errors
    - Reorder checks for aesthetic or performance reasons

    The evaluation order is THEOLOGICALLY AND ARCHITECTURALLY SIGNIFICANT.

    1. HAMARTIA BUFFER CHECK (Memory Leak)
       - unconfessed_count is a raw COUNT(*)
       - If >= 5 → system is CRITICAL regardless of all other inputs
       - Time does NOT reduce load

    2. ASCETIC INTEGRITY CHECK (Kernel Integrity)
       - Strict fast violations immediately escalate to CRITICAL
       - Missed prayer rule degrades the system
       - Missed prayer + existing hamartia escalates to CRITICAL

    3. SIGNAL / NOISE CHECK (Latency)
       - signal = prayer_minutes + reading_minutes
       - noise = screen_time_minutes
       - ratio < 0.1 indicates DEGRADED state
       - Perfect silence (noise == 0) is STABLE

    4. DEFAULT
       - If none of the above conditions are met, the system is STABLE

    This function RETURNS A STATE STRING.
    It does not mutate data.
    It does not store health.
    It does not recommend behavior.

    If you think this logic should be "improved," stop.
    Improvements here are philosophical changes, not refactors.

    Args:
        daily_state: Dict containing prayer_minutes, reading_minutes,
                     screen_time_minutes, fasted, prayed flags
        liturgical_context: Dict containing fast_type (strict/regular/none),
                           feast information
        unconfessed_count: Integer count of unconfessed hamartia entries

    Returns:
        str: One of "CRITICAL", "DEGRADED", or "STABLE"
    """

    # 1. HAMARTIA BUFFER CHECK
    if unconfessed_count >= 5:
        return "CRITICAL"

    # 2. ASCETIC INTEGRITY CHECK
    fast_type = liturgical_context.get("fast_type")
    fasted = daily_state.get("fasted", False)
    prayed = daily_state.get("prayed", False)

    if fast_type == "strict" and not fasted:
        return "CRITICAL"

    if not prayed:
        if unconfessed_count > 0:
            return "CRITICAL"
        return "DEGRADED"

    # 3. SIGNAL / NOISE CHECK
    prayer_minutes = daily_state.get("prayer_minutes", 0)
    reading_minutes = daily_state.get("reading_minutes", 0)
    screen_time_minutes = daily_state.get("screen_time_minutes", 0)

    signal = prayer_minutes + reading_minutes
    noise = screen_time_minutes

    if noise == 0:
        return "STABLE"

    if noise > 0:
        ratio = signal / noise
        if ratio < 0.1:
            return "DEGRADED"

    # 4. DEFAULT
    return "STABLE"
