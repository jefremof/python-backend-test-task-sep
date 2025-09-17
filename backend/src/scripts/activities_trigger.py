ACTIVITIES_DEPTH_TRIGGER = """
    CREATE OR REPLACE FUNCTION activities_check_depth() RETURNS trigger AS $$
    DECLARE
        ancestors_count INT;
        found_cycle INT;
    BEGIN
        IF NEW.parent_id IS NULL THEN
            RETURN NEW;
        END IF;

        IF NEW.parent_id = NEW.id THEN
            RAISE EXCEPTION 'parent_id cannot be equal to own id';
        END IF;

        WITH RECURSIVE up(id) AS (
            SELECT NEW.parent_id
            UNION ALL
            SELECT a.parent_id FROM activities a JOIN up ON a.id = up.id WHERE a.parent_id IS NOT NULL
        )
        SELECT count(*) INTO ancestors_count FROM up;

        IF (ancestors_count + 1) > 3 THEN
            RAISE EXCEPTION 'Activity nesting level would exceed maximum 3 (ancestors: %)', ancestors_count;
        END IF;

        IF NEW.id IS NOT NULL THEN
            WITH RECURSIVE down(id) AS (
                SELECT id FROM activities WHERE parent_id = NEW.id
                UNION ALL
                SELECT a.id FROM activities a JOIN down ON a.parent_id = down.id
            )
            SELECT 1 INTO found_cycle FROM down WHERE id = NEW.parent_id LIMIT 1;

            IF found_cycle IS NOT NULL THEN
                RAISE EXCEPTION 'Setting parent_id would create a cycle';
            END IF;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""

SETUP_TRIGGER = """
    CREATE TRIGGER activities_parent_trigger
    BEFORE INSERT OR UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION activities_check_depth();
"""

DROP_TRIGGER = """
    DROP TRIGGER IF EXISTS activities_parent_trigger ON activities;
"""

DROP_FUNCTION = """
    DROP FUNCTION IF EXISTS activities_check_depth();
"""