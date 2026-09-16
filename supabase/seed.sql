-- ==========================================================
-- ROUGHSET CHALLENGE - SEED DATA (DEMO / TESTING)
-- Creates 1 demo classroom session and 5 sample students
-- To remove demo data:
-- DELETE FROM classroom_sessions WHERE code = 'DEMO99';
-- ==========================================================

DO $$
DECLARE
    v_classroom_id UUID;
    v_p1 UUID;
    v_p2 UUID;
    v_p3 UUID;
    v_p4 UUID;
    v_p5 UUID;
BEGIN
    -- 1. Create Demo Classroom Session
    INSERT INTO classroom_sessions (code, active, joining_open, created_at)
    VALUES ('DEMO99', TRUE, TRUE, NOW() - INTERVAL '15 minutes')
    ON CONFLICT (code) DO UPDATE SET active = TRUE
    RETURNING id INTO v_classroom_id;

    -- 2. Insert Demo Students
    INSERT INTO players (classroom_session_id, first_name, nickname, created_at)
    VALUES 
        (v_classroom_id, 'Sara', 'Sara_AI', NOW() - INTERVAL '12 minutes') RETURNING id INTO v_p1;
    INSERT INTO players (classroom_session_id, first_name, nickname, created_at)
    VALUES 
        (v_classroom_id, 'Adam', 'AdamData', NOW() - INTERVAL '11 minutes') RETURNING id INTO v_p2;
    INSERT INTO players (classroom_session_id, first_name, nickname, created_at)
    VALUES 
        (v_classroom_id, 'Lina', 'Lina_ML', NOW() - INTERVAL '10 minutes') RETURNING id INTO v_p3;
    INSERT INTO players (classroom_session_id, first_name, nickname, created_at)
    VALUES 
        (v_classroom_id, 'Youssef', 'Youssef_CS', NOW() - INTERVAL '9 minutes') RETURNING id INTO v_p4;
    INSERT INTO players (classroom_session_id, first_name, nickname, created_at)
    VALUES 
        (v_classroom_id, 'Mariem', 'Mariem_Dauphine', NOW() - INTERVAL '8 minutes') RETURNING id INTO v_p5;

    -- 3. Insert Game Progress (Scores and Times)
    INSERT INTO game_progress (player_id, current_level, score, started_at, completed_at, completed)
    VALUES
        (v_p1, 5, 2950, NOW() - INTERVAL '12 minutes', NOW() - INTERVAL '6 minutes 28 seconds', TRUE),
        (v_p2, 5, 2875, NOW() - INTERVAL '11 minutes', NOW() - INTERVAL '4 minutes 59 seconds', TRUE),
        (v_p3, 5, 2800, NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '4 minutes 02 seconds', TRUE),
        (v_p4, 5, 2650, NOW() - INTERVAL '9 minutes',  NOW() - INTERVAL '1 minute 48 seconds', TRUE),
        (v_p5, 4, 2500, NOW() - INTERVAL '8 minutes',  NULL, FALSE);

END $$;
