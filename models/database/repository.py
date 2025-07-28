from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from .schemas import JobPostingDB, JobCriteriaDB
from .connection import get_db_session
from models.job_posting import JobPosting


class JobPostingRepository:
    """Handles all database operations for job postings."""

    def __init__(self, db: Session = None):
        self.db = db if db else next(get_db_session())

    def get_all_job_ids(self) -> List[int]:
        """Get all job IDs from the database."""
        stmt = select(JobPostingDB.id)
        result = self.db.execute(stmt)
        return [row[0] for row in result.all()]

    def create_job_posting(self, job: JobPosting) -> JobPostingDB:
        """Create a single job posting from Pydantic model."""
        try:
            job_dict = job.model_dump()
            # Transform criteria to DB models
            job_dict["criteria"] = [JobCriteriaDB(job_id=job.id, **crit) for crit in job_dict["criteria"]]
            db_job = JobPostingDB(**job_dict)
            self.db.add(db_job)
            self.db.commit()
            self.db.refresh(db_job)
            return db_job
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating job posting: {str(e)}")

    def bulk_create_job_postings(self, jobs: List[JobPosting]) -> List[JobPostingDB]:
        """Bulk create job postings from Pydantic models."""
        try:
            db_jobs = []

            for job in jobs:
                job_dict = job.model_dump()
                # Transform criteria to DB models
                job_dict["criteria"] = [JobCriteriaDB(job_id=job.id, **crit) for crit in job_dict["criteria"]]
                db_jobs.append(JobPostingDB(**job_dict))

            self.db.add_all(db_jobs)
            self.db.commit()
            return db_jobs
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Bulk create failed: {str(e)}")