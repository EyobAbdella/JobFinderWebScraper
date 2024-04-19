from bs4 import BeautifulSoup
from urllib.parse import urlparse
from db import Database
import requests
import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def filter_jobs(page_number):
    url = f"https://www.ethiopianreporterjobs.com/jobs-in-ethiopia/page/{page_number}"
    try:

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        job_container = soup.find(class_="-wrap")
        time_units = ["day", "days", "week", "weeks", "month", "months"]
        jobs = job_container.find_all(class_="loop-item-wrap list")
        job_links = []
        for job in jobs:
            job_date = job.find(class_="job-date-ago").text.strip().lower()
            if any(unit in job_date for unit in time_units):
                break
            job_link = job.find(class_="loop-item-title").find("a")["href"]
            job_links.append(job_link)
        return job_links
    except Exception as e:
        logger.error(f"Failed to fetch job links for page {page_number}: {e}")
        return []


def get_job_links():
    url = "https://www.ethiopianreporterjobs.com/jobs-in-ethiopia/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        pages = soup.find_all(class_="page-numbers")
        page_number = int(pages[len(pages) - 2].text)
        job_links = []
        for page in range(2, int(page_number / 2)):
            job = filter_jobs(page)
            job_links.extend(job)
            if len(job) < 10:
                break
        return job_links
    except Exception as e:
        logger.error(f"Failed to fetch job links: {e}")
        return []


def clean_text(text):
    try:
        unwanted_class_names = [
            "addtoany_share_save_container addtoany_content addtoany_content_bottom",
            "code-block code-block-2",
            "pvc_clear",
            "pvc_stats all pvc_load_by_ajax_update",
            "pvc_clear",
        ]
        soup = BeautifulSoup(text, "html.parser")

        for unwanted_cn in unwanted_class_names:
            unwanted_element = soup.find(class_=unwanted_cn)
            unwanted_element.extract()

        return str(soup)
    except Exception as e:
        logger.error(f"Failed to clean text: {e}")
        return text


def get_id(url):
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        path_parts = path.split("/")
        return int(path_parts[-2])
    except Exception as e:
        logger.error(f"Failed to get job ID: {e}")
        return None


def job_detail(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        job_id = get_id(link)
        job_title = soup.find(class_="page-title").text.replace("\n", "")
        salary_offer = soup.find(
            class_="value-_noo_job_field_salary cf-select-value"
        ).text
        experience_level = soup.find(
            class_="value-_noo_job_field_experience_level cf-select-value"
        ).text
        years_of_experience = soup.find(
            class_="value-_noo_job_field_year_experience cf-select-value"
        ).text
        date_posted = soup.find(
            class_="value-_noo_job_field_date_posted cf-datepicker-value"
        ).text
        deadline_date = soup.find(
            class_="value-_noo_job_field_dead_line cf-datepicker-value"
        ).text

        job_location = soup.find(class_="job-location").text.replace("\n", "")

        job_type = soup.find(class_="job-type").text

        job_category = soup.find(class_="job-category").text.replace("\n", "")

        job_requirement_and_how_to_apply = soup.find(class_="map-style-2")
        application_process = clean_text(
            job_requirement_and_how_to_apply.prettify().replace("\n", "")
        )
        job = {
            "job_id": job_id,
            "title": job_title,
            "salary_offer": salary_offer,
            "experience_level": experience_level,
            "years_of_experience": years_of_experience,
            "date_posted": date_posted,
            "deadline_date": deadline_date,
            "job_location": job_location,
            "job_type": job_type,
            "job_category": job_category,
            "application_process": application_process,
        }
        return job
    except Exception as e:
        logger.error(f"Failed to get job detail: {e}")
        return None


def save_on_database():
    try:
        jobs = get_job_links()
        data = []
        for job in jobs:
            detail = job_detail(job)
            data.append(detail)
        return data
    except Exception as e:
        logger.error(f"Failed to save jobs on database: {e}")
        return []


if __name__ == "__main__":
    job_data = save_on_database()
    if job_data:
        database = Database(job_data)
        database.insert_jobs()
        database.close()
        logger.info("Data saved successfully.")
    else:
        logger.error("No job data to save.")
