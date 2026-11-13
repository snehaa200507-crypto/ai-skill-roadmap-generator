# 🎓 AI Skill Development Roadmap Generator

An AI-powered web application that generates personalized skill development roadmaps based on a student's career goals, current skill level, daily available time, budget, and learning preferences.

The application helps students plan their learning journey through structured weekly roadmaps, practical assignments, learning resources, and progress tracking.

## 🚀 Features

- **AI-Powered Roadmap Generation:** Generates personalized learning roadmaps using Gemini AI.
- **Student Profile:** Save and manage student information and learning preferences.
- **My Roadmaps:** View and manage previously generated roadmaps.
- **Weekly Learning Plans:** Get structured topics and practical assignments.
- **Learning Resources:** Access useful learning materials.
- **Progress Tracking:** Mark completed tasks and monitor learning progress.
- **Advanced Analytics:** View learning statistics and progress insights.
- **PDF Export:** Download generated roadmaps as PDF files.
- **Database Management:** Store student profiles, roadmaps, and task progress using SQLite.

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini AI
- SQLite
- Pydantic
- ReportLab
- HTML and CSS

## 📁 Project Structure

```text
ai-skill-roadmap-generator/
│
├── app.py
├── database.py
├── pdf_helper.py
├── roadmap_data.py
├── roadmap_model.py
├── requirements.txt
├── .gitignore
│
└── utils/
    ├── ai_helper.py
    └── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/snehaa200507-crypto/ai-skill-roadmap-generator.git
```

### 2. Open the project folder

```bash
cd ai-skill-roadmap-generator
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Gemini API

Create a `.env` file in the project folder and add your Gemini API key using the environment variable name expected by `utils/ai_helper.py`.

**Important:** Never upload your API key or `.env` file to GitHub.

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🎯 Project Objective

The main objective of this project is to help students identify suitable learning paths and develop career-related skills through AI-generated personalized roadmaps.

It aims to make skill development more structured, accessible, and manageable.

## 👩‍💻 Project Team

| Team Member | Role |
|---|---|
| Sneha | Team Leader |
| Mehak Sharma | Data Lead |
| Mehakpreet Kaur | Model Builder |
| Nilu Kumari | Research and Testing |
| Riya | Presentation and Demo |

## 🔮 Future Scope

- More AI-powered career recommendations.
- Additional learning resource integrations.
- Personalized assessments and quizzes.
- Improved analytics and reporting.
- Deployment as a publicly accessible web application.

## 👩‍🎓 Project Information

**Project Name:** AI Skill Development Roadmap Generator  
**Domain:** Education  
**Project Type:** AI-Based Web Application  
**Developed Using:** Python and Streamlit

## 📌 Repository

[GitHub – AI Skill Development Roadmap Generator](https://github.com/snehaa200507-crypto/ai-skill-roadmap-generator)

---

**Developed as a BCA Academic Project.**
