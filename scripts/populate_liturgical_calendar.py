#!/usr/bin/env python3
"""
Populate liturgical calendar using Orthodox fasting rules.

"Let him who is on the housetop not go down." (Mark 13:15)
The calendar is upstream truth. Do not rely on memory.
"""

from datetime import date, timedelta
import sys
import os

# Ensure we can import from logos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logos.db import get_connection

# Paschalion calculation (simplified - full version would use Orthodox Easter algorithm)
GREAT_LENT_2026 = (date(2026, 3, 2), date(2026, 4, 18))
APOSTLES_FAST_2026 = (date(2026, 6, 1), date(2026, 6, 28))
DORMITION_FAST = (8, 1, 8, 14)  # Aug 1-14 every year
NATIVITY_FAST = (11, 28, 12, 24)  # Nov 28 - Dec 24 every year

def get_fast_type(d: date) -> str:
    """Determine fast type for given date."""
    # Great Lent (strict)
    if GREAT_LENT_2026[0] <= d <= GREAT_LENT_2026[1]:
        return 'strict'
    
    # Wednesday/Friday (regular)
    if d.weekday() in [2, 4]:  # 0=Mon, 2=Wed, 4=Fri
        return 'regular'
    
    # Dormition Fast (regular)
    if d.month == DORMITION_FAST[0] and DORMITION_FAST[1] <= d.day <= DORMITION_FAST[3]:
        return 'regular'
    
    # Nativity Fast (regular)
    if (d.month == NATIVITY_FAST[0] and d.day >= NATIVITY_FAST[1]) or \
       (d.month == NATIVITY_FAST[2] and d.day <= NATIVITY_FAST[3]):
        return 'regular'
    
    return 'none'

def populate_year(year: int):
    """Populate entire year."""
    conn = get_connection()
    cur = conn.cursor()
    
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    current = start
    
    print(f"Populating liturgical calendar for {year}...", end='', flush=True)
    
    count = 0
    while current <= end:
        cur.execute("""
            INSERT INTO liturgical_calendar (date, fast_type)
            VALUES (%s, %s)
            ON CONFLICT (date) DO UPDATE SET fast_type = EXCLUDED.fast_type
        """, (current, get_fast_type(current)))
        current += timedelta(days=1)
        count += 1
    
    conn.commit()
    print(f" Done ({count} days).")

if __name__ == "__main__":
    populate_year(2026)
    populate_year(2027)  # Stay ahead
