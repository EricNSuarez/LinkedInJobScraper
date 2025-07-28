from sqlalchemy import Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class JobCriteriaDB(Base):
    """Normalized job criteria table."""
    __tablename__ = "job_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"))
    key: Mapped[str] = mapped_column(String(100), index=True)
    value: Mapped[str] = mapped_column(String(255))

    job: Mapped["JobPostingDB"] = relationship(back_populates="criteria")


class JobPostingDB(Base):
    """SQLAlchemy model for job postings table."""
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    posting_date: Mapped[str] = mapped_column(String(10), nullable=True)
    scrapped_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    number_of_applicants: Mapped[str] = mapped_column(String(50), nullable=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=True)
    seniority: Mapped[str] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(100), nullable=True)
    job_function: Mapped[str] = mapped_column(String(100), nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)

    criteria: Mapped[List[JobCriteriaDB]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title='{self.title}')>"
