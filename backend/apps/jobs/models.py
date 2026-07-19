from django.db import models
from apps.common.models import BaseModel
from apps.resumes.models import Resume


class JobRecommendation(BaseModel):
    """
    Stores a recommended job matching the candidate's active resume.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="job_recommendations",
        verbose_name="Resume"
    )
    title = models.CharField(max_length=255, verbose_name="Job Title")
    score = models.IntegerField(default=0, verbose_name="Match Score")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Salary Range")
    industry = models.CharField(max_length=255, blank=True, verbose_name="Industry")
    country = models.CharField(max_length=100, blank=True, verbose_name="Country")
    remote = models.BooleanField(default=False, verbose_name="Remote Eligible")
    missing_skills = models.JSONField(default=list, blank=True, verbose_name="Missing Skills")

    class Meta(BaseModel.Meta):
        verbose_name = "Job Recommendation"
        verbose_name_plural = "Job Recommendations"
        ordering = ["-score", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.score}%) - Resume #{self.resume_id}"


class SkillGap(BaseModel):
    """
    Persists specific identified missing skill gaps for a candidate.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="skill_gaps",
        verbose_name="Resume"
    )
    skill = models.CharField(max_length=150, verbose_name="Skill Name")
    importance = models.CharField(
        max_length=50,
        default="Medium",
        verbose_name="Importance Level"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Skill Gap"
        verbose_name_plural = "Skill Gaps"
        unique_together = ("resume", "skill")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.skill} ({self.importance}) - Resume #{self.resume_id}"


class JobATSReport(BaseModel):
    """
    Persists evaluation of a resume against a specific Job Description.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="job_ats_reports",
        verbose_name="Resume"
    )
    job_title = models.CharField(max_length=255, verbose_name="Job Title")
    company_name = models.CharField(max_length=255, blank=True, verbose_name="Company Name")
    job_description = models.TextField(verbose_name="Job Description")
    
    # Core match results
    overall_match = models.IntegerField(default=0, verbose_name="Overall Match %")
    ats_score = models.IntegerField(default=0, verbose_name="ATS Score %")
    interview_readiness = models.CharField(max_length=100, default="Needs Improvement", verbose_name="Interview Readiness")
    
    # Dimension matches
    role_match = models.IntegerField(default=0, verbose_name="Role Match %")
    skills_match = models.IntegerField(default=0, verbose_name="Skills Match %")
    experience_match = models.IntegerField(default=0, verbose_name="Experience Match %")
    education_match = models.IntegerField(default=0, verbose_name="Education Match %")
    projects_match = models.IntegerField(default=0, verbose_name="Projects Match %")
    
    # Lists
    missing_skills = models.JSONField(default=list, blank=True, verbose_name="Missing Skills")
    recommendations = models.JSONField(default=list, blank=True, verbose_name="Recommendations")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Report Metadata")

    class Meta(BaseModel.Meta):
        verbose_name = "Job ATS Report"
        verbose_name_plural = "Job ATS Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_title} at {self.company_name} - Match: {self.overall_match}%"


class InterviewReadiness(BaseModel):
    """
    Persists interview readiness metrics and feedback across dimensions.
    """
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="interview_readiness_records",
        verbose_name="Resume"
    )
    job_title = models.CharField(max_length=255, verbose_name="Job Title")
    
    technical_score = models.IntegerField(default=0, verbose_name="Technical Skills Score")
    projects_score = models.IntegerField(default=0, verbose_name="Projects Score")
    experience_score = models.IntegerField(default=0, verbose_name="Experience Score")
    leadership_score = models.IntegerField(default=0, verbose_name="Leadership Score")
    communication_score = models.IntegerField(default=0, verbose_name="Communication Score")
    
    overall_readiness = models.CharField(max_length=100, verbose_name="Overall Readiness Status")
    feedback = models.JSONField(default=list, blank=True, verbose_name="Detailed Feedback")

    class Meta(BaseModel.Meta):
        verbose_name = "Interview Readiness"
        verbose_name_plural = "Interview Readiness Records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Interview Readiness for {self.job_title} - Status: {self.overall_readiness}"

