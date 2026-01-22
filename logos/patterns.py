"""
Pattern Detection for Spiritual Direction.

"By their fruits you will know them." (Matthew 7:16)
The system should surface patterns the nous cannot see.
"""

from logos.db import get_connection

def analyze_hamartia_patterns(conn=None):
    """
    Detect patterns in sin that require spiritual father review.
    
    Args:
        conn: Optional database connection (will create new if None)
        
    Returns:
        dict: Pattern analysis results
    """
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True
        
    try:
        cur = conn.cursor()
        
        # 1. Dominant passion
        cur.execute("""
            SELECT po.name, COUNT(*) as count
            FROM hamartia_log hl
            JOIN passion_ontology po ON hl.passion_id = po.id
            WHERE hl.confessed = FALSE
            GROUP BY po.name
            ORDER BY count DESC
            LIMIT 1
        """)
        dominant = cur.fetchone()
        
        # 2. Time-of-day pattern
        cur.execute("""
            SELECT 
                CASE 
                    WHEN EXTRACT(HOUR FROM created_at) BETWEEN 0 AND 5 THEN 'late_night'
                    WHEN EXTRACT(HOUR FROM created_at) BETWEEN 6 AND 11 THEN 'morning'
                    WHEN EXTRACT(HOUR FROM created_at) BETWEEN 12 AND 17 THEN 'afternoon'
                    ELSE 'evening'
                END as time_period,
                COUNT(*) as count
            FROM hamartia_log
            WHERE confessed = FALSE
            GROUP BY time_period
            ORDER BY count DESC
            LIMIT 1
        """)
        peak_time = cur.fetchone()
        
        # 3. Causal chains (passion A -> passion B within 24h)
        cur.execute("""
            SELECT 
                po1.name as first,
                po2.name as second,
                COUNT(*) as occurrences
            FROM hamartia_log hl1
            JOIN hamartia_log hl2 ON 
                hl2.created_at > hl1.created_at AND
                hl2.created_at < hl1.created_at + INTERVAL '24 hours'
            JOIN passion_ontology po1 ON hl1.passion_id = po1.id
            JOIN passion_ontology po2 ON hl2.passion_id = po2.id
            WHERE hl1.confessed = FALSE AND hl2.confessed = FALSE
                AND po1.name != po2.name
            GROUP BY po1.name, po2.name
            HAVING COUNT(*) >= 2
            ORDER BY occurrences DESC
            LIMIT 1
        """)
        chain = cur.fetchone()
        
        # 4. Correlation with screen time
        cur.execute("""
            SELECT 
                ds.screen_time_entertainment > 60 as high_entertainment,
                COUNT(hl.id) as sin_count
            FROM daily_state ds
            LEFT JOIN hamartia_log hl ON hl.date = ds.date AND hl.confessed = FALSE
            WHERE ds.date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY high_entertainment
        """)
        screen_correlation_data = dict(cur.fetchall())
        # Check if high entertainment correlates with more sin
        has_correlation = screen_correlation_data.get(True, 0) > screen_correlation_data.get(False, 0)
        
        return {
            "dominant_passion": dominant[0] if dominant else None,
            "dominant_count": dominant[1] if dominant else 0,
            "peak_time": peak_time[0] if peak_time else None,
            "causal_chain": f"{chain[0]} -> {chain[1]} ({chain[2]}x)" if chain else None,
            "screen_correlation": has_correlation
        }
        
    finally:
        if should_close:
            cur.close()
            conn.close()
