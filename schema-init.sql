-- Insert today's required initial state (runs after schema.sql)

INSERT INTO daily_state (date, prayer_minutes, reading_minutes, screen_time_minutes, fasted, prayed)
VALUES (CURRENT_DATE, 0, 0, 0, FALSE, FALSE)
ON CONFLICT (date) DO NOTHING;

INSERT INTO liturgical_calendar (date, fast_type)
VALUES (CURRENT_DATE, 'regular')
ON CONFLICT (date) DO NOTHING;
