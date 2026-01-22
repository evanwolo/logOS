"""
LogOS Alignment Module (Phase 4: Diagnostic)

"Examine yourselves as to whether you are in the faith. Test yourselves." (2 Cor 13:5)

This logic moves beyond legal standing (STABLE/CRITICAL) to spiritual diagnosis.
It identifies the passions at work and evaluates the quality of the struggle.
"""

def calculate_system_state(daily_state, liturgical_context, unconfessed_count):
    """
    LogOS Alignment Function — ORTHODOX DIAGNOSTIC SPEC

    This function evaluates the soul's condition based on the Fathers' understanding
    of virtue (arete) and vice (kakia).

    Args:
        daily_state: Dict containing prayer quality, fasting intent, screen breakdown.
        liturgical_context: Fasting rules and Feasts.
        unconfessed_count: Number of unhealed wounds.

    Returns:
        dict: A diagnostic report containing 'state', 'primary_passion', and 'counsel'.
    """
    
    # -------------------------------------------------------------------------
    # 1. THE FOUNDATION: HAMARTIA (The Burden)
    # "My iniquities have gone over my head; like a heavy burden they are too heavy for me." (Psalm 38:4)
    # -------------------------------------------------------------------------
            "state": "CRITICAL",
            "diagnosis": "Paralysis of the Will",
            "counsel": "Go to confession immediately. Do not delay. (James 5:16)",
            "metrics": None
        }

    # -------------------------------------------------------------------------
    # 2. ASCETIC INTEGRITY: FASTING (The Will)
    # "But I discipline my body and bring it into subjection." (1 Cor 9:27)
    # -------------------------------------------------------------------------
    fast_type = liturgical_context.get("fast_type")
    fasted = daily_state.get("fasted", False)
    break_reason = daily_state.get("fast_break_reason", "none")

    if fast_type == "strict" and not fasted:
        # We judge the intent, not just the act.
        if break_reason == "charity":
            # "I desire mercy and not sacrifice." (Hosea 6:6)
            # Breaking fast for hospitality is not a sin (St. John Cassian).
            pass 
        elif break_reason == "necessity":
            # "The spirit is willing, but the flesh is weak." (Matt 26:41)
            # Illness or inability is not rebellion.
            return {
                "state": "DEGRADED",
                "diagnosis": "Bodily Weakness",
                "counsel": "Do not despair. Resume the struggle tomorrow.",
                "metrics": None
            }
        else: # temptation or ignorance
            # "For Esau, who for one morsel of food sold his birthright." (Heb 12:16)
            return {
                "state": "CRITICAL",
                "diagnosis": "Gluttony/Rebellion",
                "counsel": "The belly is an ungrateful master. Fast strictly tomorrow.",
                "metrics": None
            }

    # -------------------------------------------------------------------------
    # 3. THE NOUS: PRAYER (The Connection)
    # "Pray without ceasing." (1 Thess 5:17)
    # -------------------------------------------------------------------------
    prayed = daily_state.get("prayed", False)
    # Use objective interruptions rather than subjective quality to avoid prelest
    interruptions = daily_state.get("prayer_interruptions", 0)
    
    if not prayed:
        # "Apart from Me you can do nothing." (John 15:5)
        if unconfessed_count > 0:
            return {
                "state": "CRITICAL", 
                "diagnosis": "Spiritual Death",
                "counsel": "You are cutting yourself off from the Source of Life.",
                "metrics": None
            }
        return {
            "state": "DEGRADED",
            "diagnosis": "Negligence",
            "counsel": "Force yourself to pray even briefly. The Kingdom is taken by force. (Matt 11:12)",
            "metrics": None
        }

    # Qualitative Analysis via Interruptions
    if interruptions > 2:
        # "This people honors me with their lips..." (Matt 15:8)
        # We do not fail the user, but we warn them.
        return {
            "state": "DEGRADED",
            "diagnosis": "Captivity of the Mind",
            "counsel": "Your mind is wandering. Shorten the rule, increase the attention. (St. John Climacus)",
            "metrics": None
        }

    # -------------------------------------------------------------------------
    # 4. NEPSIS: SIGNAL/NOISE (The Watchfulness)
    # "Be sober, be vigilant; because your adversary the devil walks about..." (1 Peter 5:8)
    # -------------------------------------------------------------------------
    # Signal: Prayer + Reading + Edifying Content
    signal = (
        daily_state.get("prayer_minutes", 0) + 
        daily_state.get("reading_minutes", 0) + 
        daily_state.get("screen_time_edifying", 0)
    )
    
    # Noise: Social + Entertainment (Work is neutral/necessary)
    noise = (
        daily_state.get("screen_time_social", 0) + 
        daily_state.get("screen_time_entertainment", 0)
    )

    ratio = signal / noise if noise > 0 else float('inf')

    # Metrics bundle for CLI
    metrics = {
        "signal": signal,
        "noise": noise,
        "ratio": ratio,
        "unconfessed": unconfessed_count,
        "interruptions": interruptions
    }

    if noise > 0 and ratio < 0.1:
        return {
            "state": "DEGRADED",
            "diagnosis": "Acedia / Distraction",
            "counsel": "You are fleeing the cell of your heart. Put down the device.",
            "metrics": metrics
        }

    # -------------------------------------------------------------------------
    # 5. THEOSIS (The Goal)
    # "I have fought the good fight, I have finished the race, I have kept the faith." (2 Tim 4:7)
    # -------------------------------------------------------------------------
    return {
        "state": "STABLE",
        "diagnosis": "Watchfulness",
        "counsel": "Glory to God. Do not become proud of this stability.",
        "metrics": metrics
    }
