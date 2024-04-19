from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


class Database:
    def __init__(self, jobs):
        self.jobs = jobs
        self.db = mysql.connector.connect(
            host=db_host, user=db_user, password=db_password, database="job_finder"
        )
        self.cursor = self.db.cursor()

    def setup_database_and_table(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS job_finder")
        self.cursor.execute("USE job_finder")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INT AUTO_INCREMENT NOT NULL UNIQUE,
                job_id INT NOT NULL UNIQUE,
                title VARCHAR(255) NOT NULL,
                salary_offer VARCHAR(255) NOT NULL,
                experience_level VARCHAR(255) NOT NULL,
                years_of_experience VARCHAR(255) NOT NULL,
                date_posted VARCHAR(200) NOT NULL,
                deadline_date VARCHAR(200) NOT NULL,
                job_location VARCHAR(255) NOT NULL,
                job_type VARCHAR(255),
                job_category VARCHAR(255),
                application_process TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        self.db.commit()

    def get_existing_job_ids(self):
        self.cursor.execute("SELECT job_id FROM jobs")
        return [row[0] for row in self.cursor.fetchall()]

    def insert_jobs(self):
        existing_job_ids = self.get_existing_job_ids()
        new_jobs = [job for job in self.jobs if job["job_id"] not in existing_job_ids]
        for job in new_jobs:
            self.cursor.execute(
                """
                INSERT INTO jobs (job_id, title, salary_offer, experience_level, years_of_experience, date_posted, deadline_date, job_location, job_type, job_category, application_process)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)           
                """,
                (
                    job.get("job_id"),
                    job.get("title"),
                    job.get("salary_offer"),
                    job.get("experience_level"),
                    job.get("years_of_experience"),
                    job.get("date_posted"),
                    job.get("deadline_date"),
                    job.get("job_location"),
                    job.get("job_type"),
                    job.get("job_category"),
                    job.get("application_process"),
                ),
            )
            self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
