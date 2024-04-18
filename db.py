from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


db = mysql.connector.connect(
    host=db_host, user=db_user, password=db_password, database="job_finder"
)

cursor = db.cursor()


class Database:
    def __init__(self, jobs):
        self.jobs = jobs

    def job_exits(job_id):
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE id = %s", (job_id,))
        count = cursor.fetchone()[0]
        return count > 0

    def insert_jobs(self):
        for job in self.jobs:
            cursor.execute(
                """
                INSERT INTO jobs (id, title, salary_offer, experience_level, years_of_experience, date_posted, deadline_date, job_location, job_type, job_category, application_process)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)           
                           """
            ), (
                job.id,
                job.title,
                job.salary_offer,
                job.experience_level,
                job.years_of_experience,
                job.date_posted,
                job.deadline_date,
                job.job_location,
                job.job_type,
                job.job_category,
                job.application_process,
            )
            db.commit()

    def run(self): ...

    db.close()
