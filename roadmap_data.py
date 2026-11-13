
CAREER_PATHS = {
    "Digital Marketing": {
        "description": "Learn SEO, social media marketing, content creation and analytics.",
        "skills": [
            "Digital Marketing Fundamentals",
            "SEO",
            "Social Media Marketing",
            "Content Marketing",
            "Google Analytics"
        ],
        "resources": [
            {
                "title": "Google Skillshop",
                "url": "https://skillshop.withgoogle.com/"
            },
            {
                "title": "HubSpot Academy",
                "url": "https://academy.hubspot.com/"
            }
        ]
    },

    "Web Development": {
        "description": "Learn frontend and backend web development.",
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "Python",
            "Database Basics"
        ],
        "resources": [
            {
                "title": "freeCodeCamp",
                "url": "https://www.freecodecamp.org/"
            },
            {
                "title": "W3Schools",
                "url": "https://www.w3schools.com/"
            }
        ]
    },

    "Python Development": {
        "description": "Learn Python programming and application development.",
        "skills": [
            "Python Basics",
            "Data Structures",
            "Functions",
            "Object Oriented Programming",
            "Projects"
        ],
        "resources": [
            {
                "title": "Python Official Tutorial",
                "url": "https://docs.python.org/3/tutorial/"
            },
            {
                "title": "Programiz",
                "url": "https://www.programiz.com/python-programming"
            }
        ]
    },

    "Data Science": {
        "description": "Learn data analysis, statistics and machine learning.",
        "skills": [
            "Python",
            "Statistics",
            "Pandas",
            "Data Visualization",
            "Machine Learning"
        ],
        "resources": [
            {
                "title": "Kaggle Learn",
                "url": "https://www.kaggle.com/learn"
            },
            {
                "title": "Google Machine Learning",
                "url": "https://developers.google.com/machine-learning"
            }
        ]
    }
}


def get_career_paths():
    return list(CAREER_PATHS.keys())


def get_career_details(career_goal):
    return CAREER_PATHS.get(career_goal, {})


if __name__ == "__main__":
    print("Available Career Paths:")

    for career in get_career_paths():
        print("-", career)

    print("\nDigital Marketing Details:")
    print(get_career_details("Digital Marketing"))
