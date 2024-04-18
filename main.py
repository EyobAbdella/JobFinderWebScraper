from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


def job_listing(page_number):
    url = f"https://www.ethiopianreporterjobs.com/jobs-in-ethiopia/page/{page_number}"
    page = requests.get(url)

    soup = BeautifulSoup(page.text, "html.parser")

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


def get_job():
    url = "https://www.ethiopianreporterjobs.com/jobs-in-ethiopia/"
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    pages = soup.find_all(class_="page-numbers")
    page_number = int(pages[len(pages) - 2].text)
    job_links = []
    for page in range(4, int(page_number / 2)):
        job = job_listing(page)
        job_links.extend(job)
        if len(job) < 10:
            break
    return job_links


def clean_code(code):
    unwanted_class_names = [
        "addtoany_share_save_container addtoany_content addtoany_content_bottom",
        "code-block code-block-2",
        "pvc_clear",
        "pvc_stats all pvc_load_by_ajax_update",
        "pvc_clear",
    ]
    soup = BeautifulSoup(code, "html.parser")

    for unwanted_cn in unwanted_class_names:
        unwanted_element = soup.find(class_=unwanted_cn)
        unwanted_element.extract()

    return str(soup)


def get_id(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    path_parts = path.split("/")
    return int(path_parts[-2])


def job_detail(link):
    # Check the job exists before creating it on the database by comparing the last job ID with the new one
    detail = requests.get(link)
    soup = BeautifulSoup(detail.text, "html.parser")
    id = get_id(link)
    job_title = soup.find(class_="page-title").text.replace("\n", "")
    salary_offer = soup.find(class_="value-_noo_job_field_salary cf-select-value").text
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

    # Use Rich Text Editor to display
    job_requirement_and_how_to_apply = soup.find(class_="map-style-2")
    application_process = clean_code(
        job_requirement_and_how_to_apply.prettify().replace("\n", "")
    )
    job = {
        "id": id,
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


def insert_job(job): ...
def job_exists(job_id): ...


def save_on_database():
    jobs = get_job()
    for job in jobs:
        detail = job_detail(job)
        print(detail)
        break


save_on_database()
