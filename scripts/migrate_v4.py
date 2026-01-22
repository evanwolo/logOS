#!/usr/bin/env python3
"""
LogOS Phase 4 Migration: The Ontological Shift.

"Be transformed by the renewing of your mind." (Romans 12:2)

This script alters the schema to reflect Orthodox anthropology:
1. The passions are interconnected (Evagrius).
2. Confession is a sacrament, not a toggle (St. John Chrysostom).
3. Prayer is qualitative communion, not quantitative fulfillment (Theophan the Recluse).
"""

import sys
import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("LOGOS_DB_HOST", "localhost"),
        port=os.environ.get("LOGOS_DB_PORT", "5432"),
        database=os.environ.get("LOGOS_DB_NAME", "logos"),
        user=os.environ.get("LOGOS_DB_USER", "logos"),
        password=os.environ.get("LOGOS_DB_PASSWORD", ""),
    )

def migrate():
    conn = get_connection()
    cur = conn.cursor()
    
    print("Initiating ontologial transformation of schema...")

    # ---------------------------------------------------------
    # 1. PASSION ONTOLOGY (The Root System)
    # Justification: "The fear of the Lord is the beginning of wisdom." (Prov 9:10)
    # We cannot fight symptoms; we must identify the root logismoi (thoughts).
    # ---------------------------------------------------------
    print("Creating passion_ontology (Evagrian hierarchy)...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passion_ontology (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK (type IN ('bodily', 'spiritual', 'root')),
            parent_passion_id INTEGER REFERENCES passion_ontology(id),
            description TEXT
        );
    """)

    # Seeding the 8 Logismoi (Evagrius Ponticus, Praktikos)
    # The passions are not a flat list but a genealogy of evil.
    print("Seeding the 8 Logismoi...")
    cur.execute("""
        INSERT INTO passion_ontology (name, type, parent_passion_id) VALUES
        ('Pride', 'root', NULL),       -- The head of the dragon (Sirach 10:13)
        ('Vainglory', 'spiritual', NULL), -- Prepares the way for Pride (St. John Cassian)
        ('Acedia', 'spiritual', NULL),    -- The noonday demon (Psalm 90:6)
        ('Anger', 'spiritual', NULL),     -- Cuts off prayer (1 Timothy 2:8)
        ('Sadness', 'spiritual', NULL),   -- Worldly sorrow brings death (2 Cor 7:10)
        ('Avarice', 'spiritual', NULL),   -- Root of all evils (1 Tim 6:10)
        ('Lust', 'bodily', NULL),         -- Wars against the soul (1 Peter 2:11)
        ('Gluttony', 'bodily', NULL)      -- The stomach's demands (Phil 3:19)
        ON CONFLICT (name) DO NOTHING;
    """)

    # ---------------------------------------------------------
    # 2. HAMARTIA LOG REFINEMENT
    # Justification: "See if there is any wicked way in me." (Psalm 139:24)
    # Sin is not an isolated event but has context and lineage.
    # ---------------------------------------------------------
    print("Refining hamartia_log for context and lineage...")
    cur.execute("""
        ALTER TABLE hamartia_log 
        ADD COLUMN IF NOT EXISTS passion_id INTEGER REFERENCES passion_ontology(id),
        ADD COLUMN IF NOT EXISTS context TEXT, 
        ADD COLUMN IF NOT EXISTS parent_sin_id INTEGER REFERENCES hamartia_log(id),
        ADD COLUMN IF NOT EXISTS absolution_id INTEGER; -- To be linked to confession_log
    """)

    # ---------------------------------------------------------
    # 3. CONFESSION LOG (Sacramental Reality)
    # Justification: "Whose sins you forgive are forgiven them." (John 20:23)
    # Confession is an event of Grace, distinct from our own record-keeping.
    # ---------------------------------------------------------
    print("Creating confession_log (Sacramental record)...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS confession_log (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            spiritual_father TEXT,
            penance_assigned TEXT,
            penance_completed BOOLEAN DEFAULT FALSE, -- "Bring forth fruits worthy of repentance" (Luke 3:8)
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # Link absolution (Foreign key added after table creation)
    cur.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_absolution') THEN
                ALTER TABLE hamartia_log
                ADD CONSTRAINT fk_absolution FOREIGN KEY (absolution_id) REFERENCES confession_log(id);
            END IF;
        END $$;
    """)

    # ---------------------------------------------------------
    # 4. DAILY STATE (Qualitative Ascesis)
    # Justification: "This people honors me with their lips, but their heart is far from me." (Matt 15:8)
    # We must measure the engagement of the heart (nous), not just the body.
    # ---------------------------------------------------------
    print("Adding qualitative dimensions to daily_state...")
    cur.execute("""
        ALTER TABLE daily_state
        -- Prayer Quality: "I will pray with the spirit, and I will pray with the understanding also." (1 Cor 14:15)
        -- We track OBJECTIVE interruptions to avoid prelest (delusion) of self-assessed "depth".
        ADD COLUMN IF NOT EXISTS prayer_quality TEXT CHECK (prayer_quality IN ('distracted', 'attentive', 'deep')),
        ADD COLUMN IF NOT EXISTS prayer_interruptions INTEGER DEFAULT 0,

        -- Fasting Intent: "When you fast, do not be like the hypocrites." (Matt 6:16)
        ADD COLUMN IF NOT EXISTS fast_break_reason TEXT CHECK (fast_break_reason IN ('temptation', 'necessity', 'charity', 'ignorance', 'none')),

        -- Screen Time (Nepsis/Watchfulness): "Be sober, be vigilant." (1 Peter 5:8)
        -- Distinguishing necessary work from the "cares of this world" (Mark 4:19)
        ADD COLUMN IF NOT EXISTS screen_time_work INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS screen_time_social INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS screen_time_entertainment INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS screen_time_edifying INTEGER DEFAULT 0;
    """)

    conn.commit()
    print("Transformation complete. The schema now reflects the struggle for theosis.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
