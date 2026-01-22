"""
LogOS Agenda Layer - Logic

Applies Spirit Core principles to work:
1. Append-only commitments.
2. Today-only execution tracking.
3. Derived health (Signal/Noise).
4. Passion-based failure diagnosis.
"""

from datetime import date
from logos.db import get_connection
from logos.mutations import PASSIONS


def commit(description, work_type, minutes):
    """
    Log a new commitment. Append-only.
    Args:
        description (str): Task description
        work_type (str): 'deep', 'shallow', or 'admin'
        minutes (int): Committed duration
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO commitment_log (date, description, type, committed_minutes)
            VALUES (CURRENT_DATE, %s, %s, %s)
            RETURNING id
        """, (description, work_type, minutes))
        
        cid = cur.fetchone()[0]
        conn.commit()
        return cid
    finally:
        cur.close()
        conn.close()


def log_work(category, minutes, encroached=False):
    """
    Update today's work state. Today-only.
    Args:
        category (str): Specific column name (e.g., 'deep_work_creative', 'shallow_work_waste')
        minutes (int): Minutes to add
        encroached (bool): If work encroached on prayer time
    """
    valid_categories = [
        'deep_work_creative', 'deep_work_analytical', 'deep_work_learning',
        'shallow_work_necessary', 'shallow_work_admin', 'shallow_work_waste'
    ]
    
    if category not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")

    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Ensure row exists
        cur.execute("""
            INSERT INTO daily_work_state (date) VALUES (CURRENT_DATE)
            ON CONFLICT (date) DO NOTHING
        """)
        
        query = f"UPDATE daily_work_state SET {category} = {category} + %s"
        params = [minutes]
        
        if encroached:
            query += ", encroached_prayer = TRUE"
            
        query += " WHERE date = CURRENT_DATE"
        
        cur.execute(query, params)
        conn.commit()
    finally:
        cur.close()
        conn.close()


def log_context_switch(from_type, to_type, passion=None, lag=0):
    """Log a context switch event."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO context_events (date, from_type, to_type, trigger_passion, resumption_lag_minutes)
            VALUES (CURRENT_DATE, %s, %s, %s, %s)
        """, (from_type, to_type, passion, lag))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def abandon_commitment(commitment_id, passion):
    """
    Mark a commitment as abandoned.
    Requires diagnosing the Passion (Root Cause).
    """
    if passion not in PASSIONS:
        raise ValueError(f"Invalid passion. Must be one of: {', '.join(PASSIONS)}")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE commitment_log 
            SET status = 'abandoned', 
                failure_passion = %s,
                processed = FALSE,
                updated_at = NOW()
            WHERE id = %s AND status = 'active'
        """, (passion, commitment_id))
        
        if cur.rowcount == 0:
            raise ValueError("Commitment not found or not active.")
            
        conn.commit()
    finally:
        cur.close()
        conn.close()


def calculate_work_health():
    """
    Derived Health for the Agenda Layer.
    FROZEN LOGIC.
    Returns: dict with 'state' and 'diagnosis'
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Get Daily State
        cur.execute("""
            SELECT 
                deep_work_creative + deep_work_analytical + deep_work_learning as signal,
                shallow_work_waste as noise,
                encroached_prayer
            FROM daily_work_state WHERE date = CURRENT_DATE
        """)
        row = cur.fetchone()
        
        signal = row[0] if row else 0
        noise = row[1] if row else 0
        encroached = row[2] if row else False
        
        # 2. Get Unprocessed Failures (Entropic Debt)
        cur.execute("SELECT COUNT(*) FROM commitment_log WHERE status = 'abandoned' AND processed = FALSE")
        debt = cur.fetchone()[0]
        
        # 3. Get Liturgical Context (Sacred Time)
        cur.execute("SELECT type FROM work_calendar WHERE date = CURRENT_DATE")
        cal_row = cur.fetchone()
        day_type = cal_row[0] if cal_row else 'regular'

        # 4. Check Unfulfilled Deep Work Promises
        cur.execute("""
            SELECT COUNT(*) FROM commitment_log 
            WHERE date = CURRENT_DATE AND type = 'deep' AND status = 'active' AND actual_minutes = 0
        """)
        unfulfilled_deep = cur.fetchone()[0]

        # --- ALIGNMENT LOGIC ---
        
        # CRITICAL: Entropic Debt
        if debt >= 5:
            return {"state": "CRITICAL", "diagnosis": "Entropic Debt (≥5 unprocessed failures)"}
            
        # CRITICAL: Hierarchy Violation
        if encroached:
            return {"state": "CRITICAL", "diagnosis": "Sacred Time Violation (Work encroached on prayer)"}
            
        # CRITICAL: Violated Sacred Time (Strict Day)
        if day_type == 'strict' and noise > 0:
            return {"state": "CRITICAL", "diagnosis": "Strict Work Day Violated (Noise detected)"}
            
        # CRITICAL: Deep Work Promised, Not Delivered, with Debt
        if unfulfilled_deep > 0 and debt > 0:
             return {"state": "CRITICAL", "diagnosis": "Broken Promises with Entropic Debt"}

        # DEGRADED: Signal/Noise Ratio
        if noise > 0:
            ratio = signal / noise
            if ratio < 1.0:  # More noise than signal
                return {"state": "DEGRADED", "diagnosis": f"High Noise Ratio ({ratio:.2f})"}
        
        return {"state": "STABLE", "diagnosis": "Nominal"}
        
    finally:
        cur.close()
        conn.close()
