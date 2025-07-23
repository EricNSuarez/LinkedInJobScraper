from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class JobPosting(BaseModel):
    id: int
    posting_date: Optional[str] = Field(default=None, description="The date the job was posted in 'dd-mm-yyyy' format.")
    scrapped_datetime: str = Field(default=None, description="Date and time the job was scrapped in 'yyyy-mm-dd hh:MM:ss' format.")
    title: Optional[str] = Field(default=None, description="The title of the job posting position.")
    company_name: Optional[str] = Field(default=None, description="The name of the company posting the job.")
    location: Optional[str] = Field(default=None, description="The job location.")
    number_of_applicants: Optional[str] = Field(default=None, description="Number of applicants for the job.")
    job_description: Optional[str] = Field(default=None, description="The description of the job.")
    seniority: Optional[str] = Field(default=None, description="The seniority level of the job.")
    employment_type: Optional[str] = Field(default=None, description="The type of employment (e.g., Full-time, Part-time).")
    job_function: Optional[str] = Field(default=None, description="The job function (e.g., Marketing, Engineering).")
    industry: Optional[str] = Field(default=None, description="The industry category of the job.")
    job_criteria: Optional[Dict[str, Any]] = Field(default=None, description="Dynamic job criteria fields.")

    def __str__(self):
        # Custom string representation to format job_scrapped_datetime
        return f'JobPosting(id={self.id}, title={self.title}, company={self.company_name}, job_scrapped_datetime={self.scrapped_datetime})'