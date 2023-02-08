# Use the official PostgreSQL image as the base image
FROM postgres:14

# Set the environment variables for the default PostgreSQL user and database
ENV POSTGRES_USER airflow
ENV POSTGRES_PASSWORD airflow
ENV POSTGRES_DB airflow

# Initialize the directory
RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

# Copy the SQL script to create the default user and database
COPY init-airflow_user-db.sql /docker-entrypoint-initdb.d/
