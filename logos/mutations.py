"""
LogOS Mutation Layer - Write Commands

Phase 4: Controlled mutation interface with Orthodox corrections.

Commands implemented:
- logos log add       : Append sin to hamartia_log (with passion_id FK)
- logos ascetic       : Update daily_state (granular fields, no revisionism)
- logos log confess   : Record the Sacrament, then absolve sins

All mutations respect temporal constraints and append-only rules.
"""

import sys
from datetime import date
from logos.db import get_connection
import psycopg2


# Canonical list of the Eight Passions (Evagrius of Pontus)
PASSIONS = [
    "Gluttony",
    "Lust", 
    "Avarice",
    "Sadness",
    "Anger",
    "Acedia",
    "Vainglory",
    "Pride"
]

# Valid fast break reasons (from migrate_v4.py)
FAST_BREAK_REASONS = ["temptation", "necessity", "charity", "ignorance", "none"]


def _get_passion_id(cur, passion_name):
    """
    Lookup the passion_id from passion_ontology.
    Returns None if not found (graceful degradation for unmigrated DBs).
    """
    try:
        cur.execute("SELECT id FROM passion_ontology WHERE name = %s", (passion_name,))
        row = cur.fetchone()
        return row[0] if row else None
    except psycopg2.Error:
        # Table may not exist in unmigrated databases
        return None


def log_hamartia(passion, description, context=None, parent_sin_id=None):
    """
    Append a sin to the hamartia_log.
    
    ORTHODOX CORRECTION (Heresy III): Now uses passion_ontology FK
    when available, while maintaining backward compatibility.
    
    Args:
        passion: One of the eight passions
        description: Description of the sin
        context: Optional context of the sin (Phase 4)
        parent_sin_id: Optional FK to parent sin (lineage tracking)
        
    Returns:
        int: New unconfessed count
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Attempt to resolve passion to FK (Orthodox)
        passion_id = _get_passion_id(cur, passion)
        
        # Insert the hamartia record (with both old string and new FK for compatibility)
        cur.execute("""
            INSERT INTO hamartia_log (date, description, passions, passion_id, context, parent_sin_id, confessed)
            VALUES (CURRENT_DATE, %s, %s, %s, %s, %s, FALSE)
        """, (description, passion, passion_id, context, parent_sin_id))
        
        # Get new unconfessed count
        cur.execute("""
            SELECT COUNT(*) FROM hamartia_log WHERE confessed = FALSE
        """)
        unconfessed_count = cur.fetchone()[0]
        
        conn.commit()
        return unconfessed_count
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"error: failed to log hamartia: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()


def update_daily_state(prayer_minutes=None, prayer_interruptions=None,
                       reading_minutes=None, 
                       screen_time_work=None, screen_time_social=None,
                       screen_time_entertainment=None, screen_time_edifying=None,
                       screen_time_minutes=None,  # Legacy field
                       fasted=None, fast_break_reason=None,
                       prayed=None):
    """
    Update today's daily_state with Phase 4 Granularity.
    
    ORTHODOX CORRECTION (Heresy I & IV):
    - Accepts all fields that alignment.py expects
    - REJECTS negative deltas (No revisionism - time is linear)
    
    Args:
        prayer_minutes: Minutes of prayer (cumulative, non-negative)
        prayer_interruptions: Number of interruptions during prayer (cumulative)
        reading_minutes: Minutes of reading (cumulative, non-negative)
        screen_time_work: Neutral screen time (work)
        screen_time_social: Noise - social media
        screen_time_entertainment: Noise - entertainment
        screen_time_edifying: Signal - edifying content
        screen_time_minutes: Legacy total (for backward compatibility)
        fasted: Boolean - set fasting status
        fast_break_reason: Why fast was broken (temptation/necessity/charity/ignorance/none)
        prayed: Boolean - set prayer completion status
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Ensure row exists for today
        cur.execute("""
            INSERT INTO daily_state (date)
            VALUES (CURRENT_DATE)
            ON CONFLICT (date) DO NOTHING
        """)
        
        updates = []
        params = []
        
        # Helper to prevent revisionism (Heresy IV correction)
        def add_cumulative(field, value):
            if value is not None:
                if value < 0:
                    raise ValueError(f"Cannot decrement {field}: Time is linear. You cannot un-pray or un-sin.")
                updates.append(f"{field} = COALESCE({field}, 0) + %s")
                params.append(value)

        # Prayer
        add_cumulative("prayer_minutes", prayer_minutes)
        add_cumulative("reading_minutes", reading_minutes)
        
        # Prayer quality (Phase 4)
        if prayer_interruptions is not None:
            if prayer_interruptions < 0:
                raise ValueError("Cannot have negative interruptions.")
            updates.append("prayer_interruptions = COALESCE(prayer_interruptions, 0) + %s")
            params.append(prayer_interruptions)
        
        # Screen time breakdown (Phase 4 - Signal/Noise)
        add_cumulative("screen_time_work", screen_time_work)
        add_cumulative("screen_time_social", screen_time_social)
        add_cumulative("screen_time_entertainment", screen_time_entertainment)
        add_cumulative("screen_time_edifying", screen_time_edifying)
        
        # Legacy total screen time (backward compatibility)
        add_cumulative("screen_time_minutes", screen_time_minutes)
        
        # Fasting (non-cumulative)
        if fasted is not None:
            updates.append("fasted = %s")
            params.append(fasted)
        
        if fast_break_reason is not None:
            if fast_break_reason not in FAST_BREAK_REASONS:
                raise ValueError(f"Invalid fast_break_reason. Must be one of: {', '.join(FAST_BREAK_REASONS)}")
            updates.append("fast_break_reason = %s")
            params.append(fast_break_reason)
        
        if prayed is not None:
            updates.append("prayed = %s")
            params.append(prayed)
        
        if updates:
            query = f"""
                UPDATE daily_state
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE date = CURRENT_DATE
            """
            cur.execute(query, params)
        
        conn.commit()
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"error: failed to update daily state: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()


def fetch_unconfessed_sins():
    """
    Retrieve all unconfessed sins.
    
    Returns:
        list: List of dicts with id, date, description, passions
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, date, description, passions
            FROM hamartia_log
            WHERE confessed = FALSE
            ORDER BY date ASC, id ASC
        """)
        
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "date": row[1],
                "description": row[2],
                "passions": row[3]
            }
            for row in rows
        ]
        
    except psycopg2.Error as e:
        print(f"error: failed to fetch unconfessed sins: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()


def record_sacrament(spiritual_father, penance_assigned=None, notes=None, sin_ids=None):
    """
    Record the EVENT of confession (The Sacrament).
    
    ORTHODOX CORRECTION (Heresy II): Confession is an event of Grace,
    not a boolean toggle. This creates the sacramental record FIRST,
    then links the absolved sins to it.
    
    "Whose sins you forgive are forgiven them." (John 20:23)
    
    Args:
        spiritual_father: Name of the priest who heard the confession
        penance_assigned: The penance given (optional but recommended)
        notes: Any notes about the confession
        sin_ids: List of hamartia_log IDs to absolve (if None, absolves all)
        
    Returns:
        dict: {confession_id, count_absolved}
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Create the Sacramental Event
        cur.execute("""
            INSERT INTO confession_log (date, spiritual_father, penance_assigned, notes)
            VALUES (CURRENT_DATE, %s, %s, %s)
            RETURNING id
        """, (spiritual_father, penance_assigned, notes))
        confession_id = cur.fetchone()[0]
        
        # 2. Absolve the Sins (Link to the Event)
        if sin_ids:
            cur.execute("""
                UPDATE hamartia_log
                SET confessed = TRUE, 
                    confessed_at = NOW(),
                    absolution_id = %s
                WHERE id = ANY(%s) AND confessed = FALSE
            """, (confession_id, sin_ids))
        else:
            # Absolve all unconfessed sins
            cur.execute("""
                UPDATE hamartia_log
                SET confessed = TRUE, 
                    confessed_at = NOW(),
                    absolution_id = %s
                WHERE confessed = FALSE
            """, (confession_id,))
        
        count = cur.rowcount
        conn.commit()
        return {"confession_id": confession_id, "count_absolved": count}
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"error: failed to record sacrament: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()


def mark_confessed(sin_ids):
    """
    DEPRECATED: Use record_sacrament() instead.
    
    This function is retained for backward compatibility only.
    It treats confession as a toggle, which is theologically incorrect.
    """
    import warnings
    warnings.warn(
        "mark_confessed() treats confession as a toggle. "
        "Use record_sacrament() which properly records the sacramental event.",
        DeprecationWarning
    )
    
    if not sin_ids:
        return 0
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Mark as confessed with timestamp (but no sacramental link)
        cur.execute("""
            UPDATE hamartia_log
            SET confessed = TRUE, confessed_at = NOW()
            WHERE id = ANY(%s) AND confessed = FALSE
        """, (sin_ids,))
        
        count = cur.rowcount
        conn.commit()
        return count
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"error: failed to mark sins as confessed: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()


def fetch_today_state():
    """
    Fetch today's daily_state for display.
    
    Returns:
        dict: Today's state including Phase 4 fields, or None if not found
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT prayer_minutes, reading_minutes, screen_time_minutes,
                   fasted, prayed,
                   prayer_interruptions, fast_break_reason,
                   screen_time_work, screen_time_social, 
                   screen_time_entertainment, screen_time_edifying
            FROM daily_state
            WHERE date = CURRENT_DATE
        """)
        
        row = cur.fetchone()
        if not row:
            return None
        
        return {
            "prayer_minutes": row[0] or 0,
            "reading_minutes": row[1] or 0,
            "screen_time_minutes": row[2] or 0,
            "fasted": row[3] or False,
            "prayed": row[4] or False,
            # Phase 4 fields
            "prayer_interruptions": row[5] or 0,
            "fast_break_reason": row[6],
            "screen_time_work": row[7] or 0,
            "screen_time_social": row[8] or 0,
            "screen_time_entertainment": row[9] or 0,
            "screen_time_edifying": row[10] or 0,
        }
        
    except psycopg2.Error as e:
        print(f"error: failed to fetch today's state: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()
