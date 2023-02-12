DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'airflow') THEN
    CREATE USER airflow WITH password 'airflow';
  END IF;
END $$;