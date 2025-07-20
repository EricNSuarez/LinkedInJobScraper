import requests
from bs4 import BeautifulSoup
import logging
import random
from typing import List, Dict

# Set logs level in format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_proxies() -> List[Dict[str, str]]:
    """
    Makes a request to the proxies endpoint and returns a list of proxies found.

    :return:
    List of proxies to use or empty list
    """
    proxy_request = requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")

    if proxy_request.status_code == 200:
        proxy_list = proxy_request.text.split("\n")
        return proxy_list
    else:
        logging.error("Failed to get proxies")
        return []

def main():
    title = "Data analyst"
    location = "Buenos Aires"
    start = 0

    proxy_list = get_proxies()

    if len(proxy_list) == 0:
        logging.error("Exiting script due to failure retrieving proxies")
        exit(1)

    # Construct the URL for LinkedIn job search
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"

    # Send a GET request to the URL and store the response
    # TODO: Set custom headers for the request
    response = requests.get(list_url, proxies={"http": random.choice(proxy_list)})
    logging.info(f"Response from {list_url}")

    # Raise error if request wasn't successful
    if response.status_code != 200:
        logging.error(f"Status Code: {response.status_code()}")
        raise Exception(f"Status Code: {response.status_code()}")

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
        job_posting_datetime = job.find("time", {"class": "job-search-card__listdate"})["datetime"] or None
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
        job_posting_datetime = job_posting["datetime"]

        # Construct the URL for each job using the job ID
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_posting_id}"

        # Send a GET request to the job URL and parse the reponse
        # TODO: Set custom headers for the request
        job_response = requests.get(job_url, proxies={"http": random.choice(proxy_list)})
        logging.info(f"Response from {job_url}")
        job_soup = BeautifulSoup(job_response.text, "html.parser")

        # Continue if request wasn't successful
        if job_response.status_code != 200:
            logging.error(f"Status Code: {job_response.status_code()} for job posting id: {job_posting_id}")
            continue

        # Create a dictionary to store job details
        job_post = {"job_id": job_posting_id, "job_datetime": job_posting_datetime}

        # Try to extract and store the job title
        try:
            job_post["job_title"] = job_soup.find("h2", {
                "class": "top-card-layout__title"}).text.strip()
        except:
            logging.info(f"Failed to get job title for {job_url}")
            job_post["job_title"] = None

        # Try to extract and store the company name
        try:
            job_post["company_name"] = job_soup.find("a", {
                "class": "topcard__org-name-link"}).text.strip()
        except:
            logging.info(f"Failed to get company name for {job_url}")
            job_post["company_name"] = None

        # Try to extract job location
        try:
            job_post["job_location"] = job_soup.find("span", {
                "class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
        except:
            logging.info(f"Failed to get job location for {job_url}")
            job_post["job_location"] = None

        # Try to extract and store the time posted
        try:
            job_post["time_posted"] = job_soup.find("span", {
                "class": "posted-time-ago__text"}).text.strip()
        except:
            logging.info(f"Failed to get time posted for {job_url}")
            job_post["time_posted"] = None

        # Try to extract and store the number of applicants
        try:
            job_post["num_applicants"] = job_soup.find("figcaption", {
                "class": "num-applicants__caption"}).text.strip()
        except:
            logging.info(f"Failed to get number of applicants for {job_url}")
            job_post["num_applicants"] = None

        # Try to extract and store the job description
        try:
            # Retrieve the text from the div element fathered by a div (class "description__text") > section element. Schematic: (div (class "description__text") > section > div).text
            job_post["job_description"] = job_soup.find("div", {"class": "description__text"}).find("section").find(
                "div").text.strip()
        except:
            logging.info(f"Failed to get job description for {job_url}")
            job_post["job_description"] = None

        # Try to extract and store the job criteria like seniority, employment type, job function and industry
        try:
            job_criteria = job_soup.find_all("li", {"class": "description__job-criteria-item"})
            job_criteria_dict = {}
            for criteria in job_criteria:
                criteria_field = criteria.find("h3", {"class": "description__job-criteria-subheader"}).text.strip()
                criteria_value = criteria.find("span", {"class": "description__job-criteria-text"}).text.strip()
                job_criteria_dict[criteria_field] = criteria_value

            job_post["job_criteria"] = job_criteria_dict
        except:
            logging.info(f"Failed to get job criteria for {job_url}")
            job_post["job_criteria"] = None

        # Append the job details to the job_list
        job_list.append(job_post)

if __name__ == "__main__":
    main()
