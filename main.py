import bs4
import requests
from bs4 import BeautifulSoup
import logging
import random
from datetime import datetime, timezone
from typing import List, Dict
from models.job_posting import JobPosting

# Set logs level in format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_proxies() -> List[str]:
    """
    Makes a request to the proxies endpoint and returns a list of proxies found.

    :return: List of proxies to use or empty list
    """
    proxy_request = requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")

    if proxy_request.status_code == 200:
        proxy_list = proxy_request.text.split("\n")
        return proxy_list
    else:
        logging.error("Failed to get proxies")
        return []

def get_job_postings_response(title: str , location: str, start: int, proxy: str = None) -> requests.Response | None:
    """
    Makes a request to the job search endpoint and return a response object.

    :param title: Title for the job/position to pass to the search endpoint.
    :param location: Location for the job/position to pass to the search endpoint.
    :param start: Value between 0 and 1000
    :param proxy: A proxy value. Defaults to None.
    :return: Response object or None
    """
    if start < 0 or start > 1000:
        raise ValueError("Invalid start value, number should an int between 0 and 1000")

    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"

    # Send a GET request to the URL and store the response
    # TODO: Set custom headers for the request
    response = requests.get(
        list_url,
        proxies=None if proxy is None else {"http": proxy}
    )
    logging.info(f"Response from {list_url}")

    # Raise error if request wasn't successful
    if response.status_code != 200:
        logging.error(f"Status Code: {response.status_code()}")
        raise Exception(f"Status Code: {response.status_code()}")

    return response


def find_element_text(page_element: BeautifulSoup | bs4.PageElement, name: str | List[str], class_: str | None, logging_message: str | None = None) -> str | None:
    """
    Looks up for the text for a html element on a page element.

    :param page_element: BeautifulSoup page element to find element from.
    :param name: Name of the tag to look for.
    :param class_: Class/classes to look for matching along with name.
    :param logging_message: Log message to write in case the element isn't found. Default None.
    :return: Trimmed text for the element found or None.

    """
    # Try to extract element
    found_element = page_element.find(name) if class_ is None else page_element.find(name, class_= class_)

    if found_element is None and logging_message:
        logging.info(logging_message)

    try:
        return found_element.text.strip()
    except AttributeError:
        return None


def get_job_data(job_posting_id: str, proxy: str = None) -> dict[str, str | None] | None:
    """
    Makes a request to the job posting endpoint and return a dictionary containing the following data.
        - id
        - scrapped_datetime
        - title
        - company_name
        - location
        - number_of_applicants
        - job_description
        - seniority
        - employment_type
        - job_function
        - industry
        - job_criteria

    :param job_posting_id:
    :param proxy: A proxy value. Defaults to None.

    :return: Dictionary containing relevant key/values or None:
    """

    # Create a dictionary to store job details
    job_post = {
        "id": job_posting_id,
        "scrapped_datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "title": None,
        "company_name": None,
        "location": None,
        "number_of_applicants": None,
        "job_description": None,
        "seniority": None,
        "employment_type": None,
        "job_function": None,
        "industry": None,
        "job_criteria": None
    }

    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_posting_id}"

    # Send a GET request to the job URL and parse the response
    # TODO: Set custom headers for the request
    job_response = requests.get(
        job_url,
        proxies=None if proxy is None else {"http": proxy}
    )
    logging.info(f"Response from {job_url}")

    job_soup = BeautifulSoup(job_response.text, "html.parser")

    # Continue if request wasn't successful
    if job_response.status_code != 200:
        logging.error(f"Status Code: {job_response.status_code()} for job posting id: {job_posting_id}")
        return None

    # Try to extract and store the job title
    job_post["title"] = find_element_text(
        job_soup,
        "h2",
        "top-card-layout__title",
        f"Failed to get job title for {job_url}"
    )

    # Try to extract and store the company name
    job_post["company_name"] = find_element_text(
        job_soup,
        "a",
        "topcard__org-name-link",
        f"Failed to get company name for {job_url}"
    )

    # Try to extract and store the job location
    job_post["location"] = find_element_text(
        job_soup,
        "span",
        "topcard__flavor topcard__flavor--bullet",
        f"Failed to get job location for {job_url}"
    )

    # Try to extract and store the number of applicants
    job_post["number_of_applicants"] = find_element_text(
        job_soup,
        ["figcaption", "span"],
        "num-applicants__caption",
        f"Failed to get number of applicants for {job_url}"
    )

    # Try to extract and store the job description
    description_section = job_soup.find("div", class_="description__text").find("section")
    if description_section is not None:
        job_post["job_description"] = find_element_text(
            description_section,
            "div",
            None,
            f"Failed to get job description for {job_url}"
        )

    # Try to extract and store the job criteria like seniority, employment type, job function and industry
    try:
        job_criteria = job_soup.find_all("li", class_="description__job-criteria-item")
        job_criteria_dict = {}
        for criteria in job_criteria:
            criteria_field = find_element_text(criteria,"h3", "description__job-criteria-subheader")
            criteria_value = find_element_text(criteria,"span","description__job-criteria-text")

            mapper = {
                "Seniority level": "seniority",
                "Employment type": "employment_type",
                "Job function": "job_function",
                "Industries": "industry"
            }

            if criteria_field in mapper:
                job_post[mapper[criteria_field]] = criteria_value
            else:
                job_criteria_dict[criteria_field] = criteria_value

        if len(job_criteria_dict) > 0:
            logging.info(f"Additional job criteria for id{job_posting_id}: {', '.join(job_criteria_dict.keys())}")

        job_post["job_criteria"] = job_criteria_dict
    except AttributeError:
        logging.info(f"Failed to get job criteria for {job_url}")
        job_post["job_criteria"] = None

    return job_post


def main():
    # TODO: Load search query from .env
    title = "\"Data analyst\""
    location = "Buenos Aires"
    start = 0

    proxy_list = get_proxies()

    if len(proxy_list) == 0:
        logging.error("Exiting script due to failure retrieving proxies")
        exit(1)

    response = get_job_postings_response(title, location, start, random.choice(proxy_list))

    # Get the HTML, parse the response and find all list items(jobs postings)
    list_data = response.text
    list_soup = BeautifulSoup(list_data, "html.parser")
    page_jobs = list_soup.find_all("li")

    logging.info(f"Found {len(page_jobs)} jobs")

    job_posting_ids = []

    # Iterate through job postings to find job ids
    for job in page_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        job_posting_id = base_card_div.get("data-entity-urn").split(":")[3]
        job_posting_datetime = job.find("time", class_="job-search-card__listdate").get("datetime", None)
        job_posting_ids.append({
            "id": job_posting_id,
            "datetime": job_posting_datetime,
        })

    logging.info(f"Found {len(job_posting_ids)} job posting ids")

    # Initialize an empty list to store job information
    job_list = []

    # Loop through the list of job IDs and get each URL
    for job_posting in job_posting_ids:

        job_posting_id = job_posting["id"]

        job_post  = get_job_data(job_posting_id, random.choice(proxy_list))

        job_post["posting_date"] = job_posting["datetime"]

        # Append the job details to the job_list
        job_list.append(JobPosting(**job_post))

if __name__ == "__main__":
    main()
