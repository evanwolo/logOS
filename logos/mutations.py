"""
LogOS Mutation Layer - Write Commands

Phase 4: Controlled mutation interface.

Commands implemented:
- logos log add       : Append sin to hamartia_log (append-only)
- logos ascetic       : Update daily_state (today only)
- logos log confess   : Mark sins as confessed (only state transition)

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


def log_hamartia(passion, description):
    """
    Append a sin to the hamartia_log.
    
    This is an append-only operation. No edits. No deletes.
    Once logged, it can only be marked as confessed.
    
    Args:
        passion: One of the eight passions
        description: Description of the sin
        
    Returns:
        int: New unconfessed count
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Insert the hamartia record
        cur.execute("""
            INSERT INTO hamartia_log (date, description, passions, confessed)
            VALUES (CURRENT_DATE, %s, %s, FALSE)
        """, (description, passion))
        
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


def update_daily_state(prayer_minutes=None, reading_minutes=None, 
                       screen_time_minutes=None, fasted=None, prayed=None):
    """
    Update today's daily_state.
    
    Temporal constraint: Can only update TODAY. No retroactive changes.
    Upserts the row if it doesn't exist.
    
    Args:
        prayer_minutes: Minutes of prayer (increments if provided)
        reading_minutes: Minutes of reading (increments if provided)
        screen_time_minutes: Minutes of screen time (increments if provided)
        fasted: Boolean - set fasting status
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
        
        # Build update query based on provided fields
        updates = []
        params = []
        
        if prayer_minutes is not None:
            updates.append("prayer_minutes = prayer_minutes + %s")
            params.append(prayer_minutes)
        
        if reading_minutes is not None:
            updates.append("reading_minutes = reading_minutes + %s")
            params.append(reading_minutes)
        
        if screen_time_minutes is not None:
            updates.append("screen_time_minutes = screen_time_minutes + %s")
            params.append(screen_time_minutes)
        
        if fasted is not None:
            updates.append("fasted = %s")
            params.append(fasted)
        
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


def mark_confessed(sin_ids):
    """
    Mark specific sins as confessed.
    
    This is the ONLY allowed state transition for hamartia_log.
    It does not delete. It does not edit. It only sets confessed=TRUE.
    
    Args:
        sin_ids: List of hamartia_log IDs to mark as confessed
        
    Returns:
        int: Number of rows updated
    """
    if not sin_ids:
        return 0
    
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Mark as confessed with timestamp
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
        dict: Today's state or None if not found
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT prayer_minutes, reading_minutes, screen_time_minutes,
                   fasted, prayed
            FROM daily_state
            WHERE date = CURRENT_DATE
        """)
        
        row = cur.fetchone()
        if not row:
            return None
        
        return {
            "prayer_minutes": row[0],
            "reading_minutes": row[1],
            "screen_time_minutes": row[2],
            "fasted": row[3],
            "prayed": row[4]
        }
        
    except psycopg2.Error as e:
        print(f"error: failed to fetch today's state: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()
