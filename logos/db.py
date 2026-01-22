"""
Database access layer for LogOS.

No ORM. No migrations. No implicit state.
All queries are explicit. All errors are loud.
"""

import os
import psycopg2
from psycopg2 import sql


def get_connection():
    """
    Establish a connection to the LogOS database.
    
    Environment variables (required):
    - LOGOS_DB_HOST
    - LOGOS_DB_PORT
    - LOGOS_DB_NAME
    - LOGOS_DB_USER
    - LOGOS_DB_PASSWORD
    
    Raises SystemExit if connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=os.environ.get("LOGOS_DB_HOST", "localhost"),
            port=os.environ.get("LOGOS_DB_PORT", "5432"),
            database=os.environ.get("LOGOS_DB_NAME", "logos"),
            user=os.environ.get("LOGOS_DB_USER", "logos"),
            password=os.environ.get("LOGOS_DB_PASSWORD", ""),
        )
        return conn
    except psycopg2.Error as e:
        print(f"error: database connection failed: {e}", flush=True)
        raise SystemExit(1)


def fetch_system_health_today():
    """
    Read system health for today from system_health_today view.
    
    Raises:
        SystemExit: If no row found, if invariants are missing, or DB error
        
    Returns:
        dict: Contains all fields required for calculate_system_state:
            - date
            - prayer_minutes
            - reading_minutes
            - screen_time_minutes
            - fasted
            - prayed
            - fast_type
            - feast
            - feast_level
            - unconfessed_count
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                date,
                prayer_minutes,
                reading_minutes,
                screen_time_minutes,
                fasted,
                prayed,
                fast_type,
                feast,
                feast_level,
                unconfessed_count,
                prayer_interruptions,
                fast_break_reason,
                screen_time_work,
                screen_time_social,
                screen_time_entertainment,
                screen_time_edifying
            FROM system_health_today
            LIMIT 1;
        """)
        
        row = cur.fetchone()
        if not row:
            print("error: no daily state found for today (missing invariant)", flush=True)
            raise SystemExit(1)
        
        result = {
            "date": row[0],
            "prayer_minutes": row[1],
            "reading_minutes": row[2],
            "screen_time_minutes": row[3],
            "fasted": row[4],
            "prayed": row[5],
            "fast_type": row[6],
            "feast": row[7],
            "feast_level": row[8],
            "unconfessed_count": row[9],
            # Phase 4 Granular Data
            "prayer_interruptions": row[10],
            "fast_break_reason": row[11],
            "screen_time_work": row[12],
            "screen_time_social": row[13],
            "screen_time_entertainment": row[14],
            "screen_time_edifying": row[15],
        }
        
        # Hard-fail on missing liturgical context
        if result["fast_type"] is None:
            print("error: no liturgical context for today (missing invariant)", flush=True)
            raise SystemExit(1)
        
        return result
        
    except psycopg2.Error as e:
        print(f"error: database query failed: {e}", flush=True)
        raise SystemExit(1)
    finally:
        cur.close()
        conn.close()
