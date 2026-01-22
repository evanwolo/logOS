"""
Data export for civilizational collapse.

"Lay up for yourselves treasures in heaven." (Matthew 6:20)
Digital systems are ephemeral. Paper endures.
"""

from datetime import date
from logos.db import get_connection

def export_to_plaintext(filepath: str):
    """Export entire spiritual log to plaintext."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        with open(filepath, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("LOGOS SPIRITUAL LOG\n")
            f.write(f"Exported: {date.today()}\n")
            f.write("=" * 70 + "\n\n")
            
            # Hamartia log
            cur.execute("""
                SELECT hl.date, po.name, hl.description, hl.confessed, hl.confessed_at
                FROM hamartia_log hl
                JOIN passion_ontology po ON hl.passion_id = po.id
                ORDER BY hl.date DESC, hl.id DESC
            """)
            
            f.write("HAMARTIA LOG (Sins)\n")
            f.write("-" * 70 + "\n")
            for row in cur.fetchall():
                status = "✓ CONFESSED" if row[3] else "✕ UNCONFESSED"
                f.write(f"[{row[0]}] {row[1]}: {row[2]} ({status})\n")
            
            # Confession history
            cur.execute("""
                SELECT date, spiritual_father, penance_assigned, penance_completed
                FROM confession_log
                ORDER BY date DESC
            """)
            
            f.write("\n\nCONFESSION HISTORY\n")
            f.write("-" * 70 + "\n")
            for row in cur.fetchall():
                status = "✓" if row[3] else "○"
                f.write(f"[{row[0]}] Fr. {row[1]}\n")
                f.write(f"  {status} Penance: {row[2]}\n")
            
            # Daily practice summary (last 30 days)
            cur.execute("""
                SELECT date, prayer_minutes, reading_minutes, 
                       screen_time_minutes, fasted, prayed
                FROM daily_state
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY date DESC
            """)
            
            f.write("\n\nDAILY PRACTICE (Last 30 Days)\n")
            f.write("-" * 70 + "\n")
            for row in cur.fetchall():
                f.write(f"[{row[0]}] Prayer: {row[1]}m | Reading: {row[2]}m | Screen: {row[3]}m\n")
                f.write(f"            Fasted: {'✓' if row[4] else '✗'} | Prayed: {'✓' if row[5] else '✗'}\n")
        
        print(f"✓ Exported to {filepath}")
        print("This file can be printed and stored offline.")
    finally:
        cur.close()
        conn.close()
