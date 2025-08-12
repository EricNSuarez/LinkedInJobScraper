# LinkedIn Job Scraper

A Python script to scrape job postings from LinkedIn using proxies. The extracted job data is intended to be stored in an SQLite database.

## Features

- Scrapes the following details from LinkedIn job postings:
  - **id**
  - **company**
  - **job description**
  - **seniority**
  - **industry**
  - **posting date**
  - **location**
  - **number of applicants**
  - **employment type**
  - **job function**
  
- Utilizes proxy servers to minimize the risk of being blocked while scraping.

## Proxy Source

This script uses a list of proxies obtained from [TheSpeedX's SOCKS List](https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EricNSuarez/LinkedInJobScraper.git
   cd LinkedInJobPostings
   ```

2. Install the required packages:
   ```bash
   uv pip install -r pyproject.toml
   ```

## Usage

To run the scraper, execute the following command:
```bash
uv run main.py
```

## Current Status

### What's Done
- [x] Job postings are successfully scraped from LinkedIn.
- [x] The following data points are extracted:
  - id
  - company
  - job description
  - seniority
  - industry
  - posting date
  - location
  - number of applicants
  - employment type
  - job function
- [x] Proxies are utilized to avoid blocks while scraping.

### To Do
- [x] Implement functionality to store scraped data into an SQLite database.
- [ ] Enhance error handling.
- [ ] Optimize scraping performance and manage rate limits.
- [x] Implement functionality to skip job postings already scrapped.

## Disclaimer

This project is intended for educational purposes only. Users are advised to comply with the Terms of Service of LinkedIn and any other website they may scrape. Make sure to review and adhere to the legal requirements and ethical standards associated with web scraping.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Special thanks to [TheSpeedX](https://github.com/TheSpeedX) for providing the proxy list used in this project.