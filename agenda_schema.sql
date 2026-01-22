-- AGENDA LAYER SCHEMA
-- Wraps the Spirit Core with work/commitment tracking.

-- 1. Work Calendar (The Temporal Hierarchy)
CREATE TABLE IF NOT EXISTS work_calendar (
    date DATE PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('strict', 'regular', 'feast')),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Commitment Review (Processing Event - Created first for FK reference)
CREATE TABLE IF NOT EXISTS commitment_review (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    commitment_ids INTEGER[] NOT NULL,
    pattern_identified TEXT,
    lesson_learned TEXT,
    adjustment_planned TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Commitment Log (Append-Only)
CREATE TABLE IF NOT EXISTS commitment_log (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('deep', 'shallow', 'admin')),
    committed_minutes INTEGER NOT NULL,
    
    -- State tracking
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    actual_minutes INTEGER DEFAULT 0,
    
    -- The connection to Spirit Core (Why did you fail?)
    failure_passion TEXT, -- References the 8 Passions if abandoned
    processed BOOLEAN DEFAULT FALSE,
    review_id INTEGER REFERENCES commitment_review(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Daily Work State (Today-Only Execution)
CREATE TABLE IF NOT EXISTS daily_work_state (
    date DATE PRIMARY KEY,
    
    -- Deep Work Breakdown (Signal)
    deep_work_creative INTEGER DEFAULT 0,
    deep_work_analytical INTEGER DEFAULT 0,
    deep_work_learning INTEGER DEFAULT 0,
    
    -- Shallow Work Breakdown (Neutral/Noise)
    shallow_work_necessary INTEGER DEFAULT 0,
    shallow_work_admin INTEGER DEFAULT 0,
    shallow_work_waste INTEGER DEFAULT 0, -- Pure noise
    
    -- Hierarchy Violation
    encroached_prayer BOOLEAN DEFAULT FALSE,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Context Events (Detailed Switching Cost)
CREATE TABLE IF NOT EXISTS context_events (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    timestamp TIMESTAMP DEFAULT NOW(),
    from_type TEXT,
    to_type TEXT,
    trigger_passion TEXT, -- If switch was caused by a passion (e.g., Acedia)
    resumption_lag_minutes INTEGER DEFAULT 0
);
