-- LogOS Schema
-- Authoritative source of truth. All data is append-only unless explicitly transitioned.

CREATE TABLE IF NOT EXISTS liturgical_calendar (
    date DATE PRIMARY KEY,
    fast_type TEXT NOT NULL CHECK (fast_type IN ('none', 'regular', 'strict')),
    feast TEXT,
    feast_level TEXT
);

CREATE TABLE IF NOT EXISTS passion_ontology (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('bodily', 'spiritual', 'root')),
    parent_passion_id INTEGER REFERENCES passion_ontology(id),
    description TEXT
);

CREATE TABLE IF NOT EXISTS confession_log (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    spiritual_father TEXT,
    penance_assigned TEXT,
    penance_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hamartia_log (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    passions TEXT NOT NULL,
    passion_id INTEGER REFERENCES passion_ontology(id),
    context TEXT,
    parent_sin_id INTEGER REFERENCES hamartia_log(id),
    absolution_id INTEGER REFERENCES confession_log(id),
    confessed BOOLEAN NOT NULL DEFAULT FALSE,
    confessed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(date, description)
);

CREATE TABLE IF NOT EXISTS daily_state (
    date DATE PRIMARY KEY,
    prayer_minutes INTEGER DEFAULT 0,
    reading_minutes INTEGER DEFAULT 0,
    screen_time_minutes INTEGER DEFAULT 0,
    
    -- Phase 4 Granular Fields
    prayer_quality TEXT CHECK (prayer_quality IN ('distracted', 'attentive', 'deep')),
    prayer_interruptions INTEGER DEFAULT 0,
    fast_break_reason TEXT CHECK (fast_break_reason IN ('temptation', 'necessity', 'charity', 'ignorance', 'none')),
    screen_time_work INTEGER DEFAULT 0,
    screen_time_social INTEGER DEFAULT 0,
    screen_time_entertainment INTEGER DEFAULT 0,
    screen_time_edifying INTEGER DEFAULT 0,
    
    fasted BOOLEAN DEFAULT FALSE,
    prayed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Read-only view for health checks
-- Computes unconfessed_count and exposes all required data for calculate_system_state
CREATE OR REPLACE VIEW system_health_today AS
SELECT
    CURRENT_DATE as date,
    ds.prayer_minutes,
    ds.reading_minutes,
    ds.screen_time_minutes,
    ds.fasted,
    ds.prayed,
    -- Granular fields for Phase 4 diagnostic
    ds.prayer_interruptions,
    ds.fast_break_reason,
    ds.screen_time_work,
    ds.screen_time_social,
    ds.screen_time_entertainment,
    ds.screen_time_edifying,
    
    lc.fast_type,
    lc.feast,
    lc.feast_level,
    COUNT(CASE WHEN h.confessed = FALSE THEN 1 END) as unconfessed_count
FROM daily_state ds
LEFT JOIN liturgical_calendar lc ON lc.date = CURRENT_DATE
LEFT JOIN hamartia_log h ON h.confessed = FALSE
GROUP BY
    ds.prayer_minutes,
    ds.reading_minutes,
    ds.screen_time_minutes,
    ds.fasted,
    ds.prayed,
    ds.prayer_interruptions,
    ds.fast_break_reason,
    ds.screen_time_work,
    ds.screen_time_social,
    ds.screen_time_entertainment,
    ds.screen_time_edifying,
    lc.fast_type,
    lc.feast,
    lc.feast_level;
