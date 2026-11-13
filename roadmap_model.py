
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List


class LearningResource(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    type: str = "Website"

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        if not value.startswith(("https://", "http://")):
            raise ValueError("Resource URL must start with http:// or https://")
        return value


class WeekPlan(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    week_number: int = Field(ge=1)
    theme: str = Field(min_length=1)
    learning_objectives: List[str] = Field(default_factory=list)
    topics: List[str] = Field(min_length=1)
    practical_assignment: str = ""
    mini_project: str = ""
    resources: List[LearningResource] = Field(default_factory=list)
    career_tip: str = ""

    @field_validator("learning_objectives", "topics")
    @classmethod
    def clean_lists(cls, values):
        return [item.strip() for item in values if item.strip()]


class Roadmap(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    description: str = ""
    estimated_duration_weeks: int = Field(ge=1)
    weeks: List[WeekPlan] = Field(min_length=8, max_length=8)

    @model_validator(mode="after")
    def validate_week_numbers(self):
        expected = list(range(1, 9))
        actual = [week.week_number for week in self.weeks]

        if actual != expected:
            raise ValueError(
                "Roadmap must contain sequential weeks from 1 to 8."
            )

        return self


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=1)
    career_goal: str = Field(min_length=1)
    skill_level: str = Field(min_length=1)
    daily_time: str = Field(min_length=1)
    budget: str = Field(min_length=1)
    preferred_language: str = "English"


def validate_roadmap(data: dict):
    """Validate AI-generated roadmap data."""
    return Roadmap.model_validate(data)


def roadmap_to_dict(roadmap: Roadmap):
    """Convert a Roadmap object into a dictionary."""
    return roadmap.model_dump()


if __name__ == "__main__":

    sample_data = {
        "title": "Digital Marketing Roadmap",
        "summary": "A beginner-friendly 8-week learning roadmap.",
        "description": "Learn digital marketing step by step.",
        "estimated_duration_weeks": 8,
        "weeks": [
            {
                "week_number": 1,
                "theme": "Digital Marketing Basics",
                "learning_objectives": [
                    "Understand digital marketing fundamentals"
                ],
                "topics": ["SEO", "Social Media Marketing"],
                "practical_assignment": "Create a sample social media post.",
                "mini_project": "Create a basic Instagram strategy.",
                "resources": [
                    {
                        "title": "Google Skillshop",
                        "url": "https://skillshop.withgoogle.com/",
                        "type": "Course"
                    }
                ],
                "career_tip": "Practice regularly."
            },
            {
                "week_number": 2,
                "theme": "Content Marketing",
                "topics": ["Content Strategy", "Content Planning"]
            },
            {
                "week_number": 3,
                "theme": "Search Engine Optimization",
                "topics": ["Keyword Research", "On-page SEO"]
            },
            {
                "week_number": 4,
                "theme": "Social Media Management",
                "topics": ["Instagram", "Facebook"]
            },
            {
                "week_number": 5,
                "theme": "Email Marketing",
                "topics": ["Email Campaigns", "Email Tools"]
            },
            {
                "week_number": 6,
                "theme": "Paid Advertising",
                "topics": ["Google Ads", "Meta Ads"]
            },
            {
                "week_number": 7,
                "theme": "Analytics",
                "topics": ["Google Analytics", "Performance Metrics"]
            },
            {
                "week_number": 8,
                "theme": "Final Project",
                "topics": ["Portfolio", "Campaign Planning"]
            }
        ]
    }

    roadmap = validate_roadmap(sample_data)

    print("Roadmap model working successfully!")
    print("Total weeks:", len(roadmap.weeks))
    print(roadmap.model_dump_json(indent=4))
