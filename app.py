
import streamlit as st

from database import (
    init_db,
    save_roadmap,
    get_all_roadmaps,
    get_roadmap,
    get_tasks,
    update_task_progress,
    get_progress_summary,
    delete_roadmap,
    save_student_profile,
    get_student_profile,
    register_user,
    authenticate_user,
    get_user_by_id
)

from utils.ai_helper import generate_roadmap

try:
    from pdf_helper import generate_roadmap_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Skill Development Roadmap Generator",
    page_icon="🎓",
    layout="wide"
)

init_db()


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>
.stApp {
    background-color: #0B1020;
    color: #FFFFFF;
}
section[data-testid="stSidebar"] {
    background-color: #151B32;
}
h1, h2, h3 {
    color: #C4B5FD !important;
}
p, label {
    color: #E5E7EB;
}
div[data-testid="stMetric"] {
    background-color: #1B2340;
    border: 1px solid #39365F;
    padding: 18px;
    border-radius: 12px;
}
.stButton button {
    background-color: #8B5CF6;
    color: white;
    border-radius: 9px;
    border: none;
    padding: 9px 18px;
}
.stButton button:hover {
    background-color: #A78BFA;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def safe_list(value):
    return value if isinstance(value, list) else []


def get_demo_roadmap(user_input):
    goal = user_input["career_goal"]

    return {
        "title": f"{goal} - Learning Roadmap",
        "summary": "A practical learning roadmap created for your career goal.",
        "description": "Demo roadmap for application testing.",
        "estimated_duration_weeks": 4,
        "weeks": [
            {
                "week_number": 1,
                "theme": "Introduction and Fundamentals",
                "learning_objectives": [
                    "Understand basic concepts",
                    "Learn important terminology"
                ],
                "topics": ["Introduction", "Basic Concepts"],
                "practical_assignment": "Prepare basic learning notes.",
                "mini_project": "Create a beginner learning plan.",
                "resources": [],
                "career_tip": "Build strong fundamentals."
            },
            {
                "week_number": 2,
                "theme": "Core Skills Development",
                "learning_objectives": [
                    "Understand core skills",
                    "Practice essential techniques"
                ],
                "topics": ["Core Skills", "Practical Learning"],
                "practical_assignment": "Complete a practical exercise.",
                "mini_project": "Create a small practice project.",
                "resources": [],
                "career_tip": "Practice consistently."
            },
            {
                "week_number": 3,
                "theme": "Advanced Practice",
                "learning_objectives": [
                    "Apply learned concepts",
                    "Improve practical knowledge"
                ],
                "topics": ["Advanced Concepts", "Tools"],
                "practical_assignment": "Work on a practical task.",
                "mini_project": "Build a sample project.",
                "resources": [],
                "career_tip": "Document your work."
            },
            {
                "week_number": 4,
                "theme": "Final Project and Career Preparation",
                "learning_objectives": [
                    "Apply all learned skills",
                    "Prepare a portfolio"
                ],
                "topics": ["Final Project", "Portfolio"],
                "practical_assignment": "Complete your final assignment.",
                "mini_project": "Create a portfolio project.",
                "resources": [],
                "career_tip": "Showcase your projects."
            }
        ]
    }


def show_roadmap(roadmap):
    st.subheader(roadmap.get("title", "Learning Roadmap"))

    st.write(
        roadmap.get("summary", roadmap.get("description", ""))
    )

    weeks = safe_list(roadmap.get("weeks", []))

    for week in weeks:
        week_number = week.get("week_number", "")

        with st.expander(
            f"Week {week_number}: {week.get('theme', 'Learning Week')}"
        ):
            st.markdown("**Learning Objectives**")
            for objective in safe_list(
                week.get("learning_objectives", [])
            ):
                st.write("•", objective)

            st.markdown("**Topics to Learn**")
            for topic in safe_list(week.get("topics", [])):
                st.write("•", topic)

            st.markdown("**Practical Assignment**")
            st.write(week.get("practical_assignment", "Not provided"))

            st.markdown("**Mini Project**")
            st.write(week.get("mini_project", "Not provided"))

            resources = safe_list(week.get("resources", []))

            if resources:
                st.markdown("**Learning Resources**")

                for resource in resources:
                    if isinstance(resource, dict):
                        title = resource.get("title", "Resource")
                        url = resource.get("url", "")
                        resource_type = resource.get("type", "Website")

                        if url.startswith(("https://", "http://")):
                            st.markdown(
                                f"- [{title}]({url}) ({resource_type})"
                            )
                        else:
                            st.write(f"- {title}")

            career_tip = week.get("career_tip", "")
            if career_tip:
                st.info(f"Career Tip: {career_tip}")


def show_pdf_download(user_input, roadmap, key):
    if not PDF_AVAILABLE:
        st.warning("PDF helper is not available.")
        return

    try:
        pdf_bytes = generate_roadmap_pdf(user_input, roadmap)

        st.download_button(
            label="📄 Download Roadmap PDF",
            data=pdf_bytes,
            file_name="AI_Learning_Roadmap.pdf",
            mime="application/pdf",
            key=key
        )

    except Exception as error:
        st.error(f"PDF generation error: {error}")



# ==================================================
# LOGIN / REGISTRATION AND USER SESSION
# ==================================================

if "user_id" not in st.session_state:
    st.title("🎓 AI Skill Development Roadmap Generator")
    st.subheader("Welcome! Login or create your student account.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input(
                "Password", type="password", key="login_password"
            )
            login_submit = st.form_submit_button(
                "Login", use_container_width=True
            )

        if login_submit:
            if not login_email.strip() or not login_password:
                st.error("Please enter your email and password.")
            else:
                account = authenticate_user(login_email, login_password)
                if account:
                    st.session_state["user_id"] = account["user_id"]
                    st.session_state["user_name"] = account["full_name"]
                    st.session_state["user_email"] = account["email"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")

    with register_tab:
        with st.form("register_form"):
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_password = st.text_input(
                "Create Password (minimum 8 characters)",
                type="password",
                key="reg_password"
            )
            reg_confirm = st.text_input(
                "Confirm Password", type="password", key="reg_confirm"
            )
            register_submit = st.form_submit_button(
                "Create Account", use_container_width=True
            )

        if register_submit:
            if not reg_name.strip() or not reg_email.strip():
                st.error("Please enter your name and email.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    new_user_id = register_user(
                        reg_name, reg_email, reg_password
                    )
                    st.session_state["user_id"] = new_user_id
                    st.session_state["user_name"] = reg_name.strip()
                    st.session_state["user_email"] = reg_email.strip().lower()
                    st.success("Account created successfully!")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except Exception as error:
                    st.error(f"Registration error: {error}")

    st.info("Each student must use their own account to keep their data private.")
    st.stop()


# Confirm that the logged-in account still exists.
current_user_id = st.session_state["user_id"]
current_account = get_user_by_id(current_user_id)

if not current_account:
    st.session_state.clear()
    st.rerun()

st.session_state["user_name"] = current_account["full_name"]
st.session_state["user_email"] = current_account["email"]


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("🎓 AI Roadmap Generator")
st.sidebar.caption("Learn • Practice • Grow")
st.sidebar.success(f"Logged in: {st.session_state['user_name']}")
st.sidebar.caption(st.session_state["user_email"])

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

PAGES = [
    "Home",
    "Student Profile",
    "Generate Roadmap",
    "My Roadmaps",
    "Learning Resources",
    "Progress Tracking",
    "Advanced Analytics"
]

# Apply a page selected by the bottom Next/Previous buttons
# before creating the sidebar radio widget.
if "pending_page" in st.session_state:
    st.session_state["selected_page"] = st.session_state.pop("pending_page")

if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "Home"

page = st.sidebar.radio(
    "Navigation",
    PAGES,
    key="selected_page"
)

st.sidebar.markdown("---")
st.sidebar.info("Your personalized AI learning companion.")


# ==================================================
# HOME / DASHBOARD
# ==================================================

if page == "Home":

    st.title("🎓 AI Skill Development Roadmap Generator")

    st.write(
        "Generate personalized learning roadmaps "
        "and track your career development."
    )

    roadmaps = get_all_roadmaps(current_user_id)

    total_roadmaps = len(roadmaps)
    total_tasks = 0
    completed_tasks = 0

    for roadmap_item in roadmaps:
        tasks = get_tasks(roadmap_item["roadmap_id"], current_user_id)
        total_tasks += len(tasks)

        completed_tasks += sum(
            1 for task in tasks
            if task.get("is_completed") == 1
        )

    pending_tasks = total_tasks - completed_tasks

    percentage = (
        round(completed_tasks / total_tasks * 100, 1)
        if total_tasks else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Roadmaps", total_roadmaps)
    col2.metric("Total Tasks", total_tasks)
    col3.metric("Completed Tasks", completed_tasks)
    col4.metric("Overall Progress", f"{percentage}%")

    st.subheader("📊 Learning Overview")

    if total_tasks:
        st.progress(percentage / 100)
        st.write(f"Completed: {completed_tasks}")
        st.write(f"Remaining: {pending_tasks}")
    else:
        st.info("Generate your first roadmap to see your progress.")

    st.subheader("🕒 Recent Roadmaps")

    if roadmaps:
        for item in roadmaps[:5]:
            st.markdown(
                f"**{item.get('roadmap_title', 'Learning Roadmap')}**"
            )
            st.caption(f"Career Goal: {item.get('career_goal', '')}")
            st.caption(f"Created: {item.get('created_at', '')}")
            st.divider()
    else:
        st.info("No roadmaps created yet.")

    profile = get_student_profile(current_user_id)

    if profile:
        st.subheader("👤 Student Profile")
        st.write(f"Welcome, **{profile['full_name']}**!")
        st.write(f"Career Goal: {profile['career_goal']}")


# ==================================================
# STUDENT PROFILE
# ==================================================

elif page == "Student Profile":

    st.title("👤 Student Profile")
    st.write("Create and manage your personal learning profile.")

    profile = get_student_profile(current_user_id) or {}

    education_options = [
        "Select Education", "Class 10", "Class 12", "Diploma",
        "BCA", "BBA", "B.Tech", "Graduate", "Postgraduate", "Other"
    ]

    skill_options = ["Beginner", "Intermediate", "Advanced"]
    time_options = [
        "30 minutes", "1 hour", "2 hours", "3 hours", "4+ hours"
    ]
    budget_options = ["Free", "Low Budget", "Medium Budget", "Flexible"]
    language_options = ["English", "Hindi", "Hinglish"]

    with st.form("student_profile_form"):

        st.subheader("Personal Information")

        full_name = st.text_input(
            "Full Name", value=profile.get("full_name", "")
        )

        email = st.text_input(
            "Account Email", value=st.session_state["user_email"], disabled=True
        )

        education = st.selectbox(
            "Education / Qualification",
            education_options,
            index=(
                education_options.index(profile.get("education"))
                if profile.get("education") in education_options else 0
            )
        )

        st.subheader("Learning Preferences")

        career_goal = st.text_input(
            "Career Goal", value=profile.get("career_goal", "")
        )

        skill_level = st.selectbox(
            "Current Skill Level",
            skill_options,
            index=(
                skill_options.index(profile.get("skill_level"))
                if profile.get("skill_level") in skill_options else 0
            )
        )

        daily_time = st.selectbox(
            "Daily Study Time",
            time_options,
            index=(
                time_options.index(profile.get("daily_time"))
                if profile.get("daily_time") in time_options else 1
            )
        )

        budget = st.selectbox(
            "Learning Budget",
            budget_options,
            index=(
                budget_options.index(profile.get("budget"))
                if profile.get("budget") in budget_options else 0
            )
        )

        preferred_language = st.selectbox(
            "Preferred Language",
            language_options,
            index=(
                language_options.index(profile.get("preferred_language"))
                if profile.get("preferred_language") in language_options else 0
            )
        )

        submitted = st.form_submit_button(
            "💾 Save / Update Profile",
            use_container_width=True
        )

        if submitted:

            if not full_name.strip():
                st.error("Please enter your full name.")

            elif not career_goal.strip():
                st.error("Please enter your career goal.")

            elif email.strip() and ("@" not in email or "." not in email):
                st.error("Please enter a valid email address.")

            else:
                profile_data = {
                    "full_name": full_name,
                    "email": email,
                    "education": education,
                    "career_goal": career_goal,
                    "skill_level": skill_level,
                    "daily_time": daily_time,
                    "budget": budget,
                    "preferred_language": preferred_language
                }

                try:
                    save_student_profile(current_user_id, profile_data)
                    st.success("Student profile saved successfully!")
                    st.rerun()

                except Exception as error:
                    st.error(f"Profile saving error: {error}")

    if profile:
        st.divider()
        st.subheader("Saved Profile Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Name:**", profile.get("full_name", ""))
            st.write("**Email:**", profile.get("email", ""))
            st.write("**Education:**", profile.get("education", ""))

        with col2:
            st.write("**Career Goal:**", profile.get("career_goal", ""))
            st.write("**Skill Level:**", profile.get("skill_level", ""))
            st.write("**Daily Time:**", profile.get("daily_time", ""))

        st.write("**Budget:**", profile.get("budget", ""))
        st.write("**Language:**", profile.get("preferred_language", ""))


# ==================================================
# GENERATE ROADMAP
# ==================================================

elif page == "Generate Roadmap":

    st.title("✨ Generate Your Learning Roadmap")

    profile = get_student_profile(current_user_id) or {}

    skill_options = ["Beginner", "Intermediate", "Advanced"]
    time_options = [
        "30 minutes", "1 hour", "2 hours", "3 hours", "4+ hours"
    ]
    budget_options = ["Free", "Low Budget", "Medium Budget", "Flexible"]
    language_options = ["English", "Hindi", "Hinglish"]

    with st.form("roadmap_form"):

        st.subheader("Student Details")

        full_name = st.text_input(
            "Full Name", value=profile.get("full_name", "")
        )

        career_goal = st.text_input(
            "Career Goal", value=profile.get("career_goal", "")
        )

        skill_level = st.selectbox(
            "Skill Level",
            skill_options,
            index=(
                skill_options.index(profile.get("skill_level"))
                if profile.get("skill_level") in skill_options else 0
            )
        )

        daily_time = st.selectbox(
            "Daily Study Time",
            time_options,
            index=(
                time_options.index(profile.get("daily_time"))
                if profile.get("daily_time") in time_options else 1
            )
        )

        budget = st.selectbox(
            "Learning Budget",
            budget_options,
            index=(
                budget_options.index(profile.get("budget"))
                if profile.get("budget") in budget_options else 0
            )
        )

        preferred_language = st.selectbox(
            "Preferred Language",
            language_options,
            index=(
                language_options.index(profile.get("preferred_language"))
                if profile.get("preferred_language") in language_options else 0
            )
        )

        generate_button = st.form_submit_button(
            "🚀 Generate My Roadmap",
            use_container_width=True
        )

    if generate_button:

        if not full_name.strip() or not career_goal.strip():
            st.error("Please enter your name and career goal.")

        else:
            user_input = {
                "full_name": full_name,
                "career_goal": career_goal,
                "skill_level": skill_level,
                "daily_time": daily_time,
                "budget": budget,
                "preferred_language": preferred_language
            }

            with st.spinner("Generating your personalized roadmap..."):

                try:
                    roadmap = generate_roadmap(user_input)

                    st.session_state["latest_roadmap"] = roadmap
                    st.session_state["latest_user_input"] = user_input
                    st.session_state["roadmap_mode"] = "AI Generated"

                except Exception as error:
                    st.warning(f"AI generation was unsuccessful: {error}")
                    st.info("Opening Demo Mode for testing.")

                    roadmap = get_demo_roadmap(user_input)

                    st.session_state["latest_roadmap"] = roadmap
                    st.session_state["latest_user_input"] = user_input
                    st.session_state["roadmap_mode"] = "Demo Mode"

            try:
                roadmap_id = save_roadmap(
                    current_user_id,
                    full_name,
                    career_goal,
                    skill_level,
                    daily_time,
                    budget,
                    st.session_state["latest_roadmap"]
                )

                st.session_state["latest_roadmap_id"] = roadmap_id
                st.success("Your roadmap has been saved successfully!")

            except Exception as error:
                st.error(f"Database saving error: {error}")

    if "latest_roadmap" in st.session_state:

        st.divider()

        mode = st.session_state.get("roadmap_mode", "Generated")
        st.caption(f"Mode: {mode}")

        show_roadmap(st.session_state["latest_roadmap"])

        show_pdf_download(
            st.session_state["latest_user_input"],
            st.session_state["latest_roadmap"],
            "latest_roadmap_pdf"
        )


# ==================================================
# MY ROADMAPS
# ==================================================

elif page == "My Roadmaps":

    st.title("📚 My Saved Roadmaps")

    roadmaps = get_all_roadmaps(current_user_id)

    if not roadmaps:
        st.info("You have not created any roadmaps yet.")

    else:
        search = st.text_input("🔍 Search by career goal")

        filtered = [
            item for item in roadmaps
            if search.lower() in item.get("career_goal", "").lower()
        ]

        if not filtered:
            st.warning("No matching roadmaps found.")

        for item in filtered:

            roadmap_id = item["roadmap_id"]

            with st.expander(
                f"📘 {item.get('roadmap_title', 'Learning Roadmap')} "
                f"— {item.get('career_goal', '')}"
            ):

                st.write("**Skill Level:**", item.get("skill_level", ""))
                st.write("**Daily Time:**", item.get("daily_time", ""))
                st.write("**Budget:**", item.get("budget", ""))
                st.write("**Created:**", item.get("created_at", ""))

                if st.button(
                    "View Full Roadmap",
                    key=f"view_{roadmap_id}"
                ):
                    selected = get_roadmap(roadmap_id, current_user_id)

                    if selected:
                        st.session_state["selected_roadmap"] = selected

                if st.button(
                    "Delete Roadmap",
                    key=f"delete_{roadmap_id}"
                ):
                    st.session_state["confirm_delete"] = roadmap_id

                if st.session_state.get("confirm_delete") == roadmap_id:

                    st.warning("Are you sure you want to delete this roadmap?")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "Yes, Delete",
                            key=f"confirm_{roadmap_id}"
                        ):
                            delete_roadmap(roadmap_id, current_user_id)
                            st.session_state.pop("confirm_delete", None)
                            st.success("Roadmap deleted.")
                            st.rerun()

                    with col2:
                        if st.button(
                            "Cancel",
                            key=f"cancel_{roadmap_id}"
                        ):
                            st.session_state.pop("confirm_delete", None)
                            st.rerun()

    selected = st.session_state.get("selected_roadmap")

    if selected:
        st.divider()
        st.subheader("Selected Roadmap")

        show_roadmap(selected["roadmap"])

        show_pdf_download(
            {
                "full_name": "",
                "career_goal": selected.get("career_goal", ""),
                "skill_level": selected.get("skill_level", ""),
                "daily_time": selected.get("daily_time", ""),
                "budget": selected.get("budget", "")
            },
            selected["roadmap"],
            f"saved_pdf_{selected['roadmap_id']}"
        )


# ==================================================
# LEARNING RESOURCES
# ==================================================

elif page == "Learning Resources":

    st.title("🌐 Learning Resources")

    st.write("Explore useful platforms to develop your skills.")

    resources = [
        (
            "Google Skillshop",
            "Google tools and digital marketing learning.",
            "https://skillshop.withgoogle.com/"
        ),
        (
            "HubSpot Academy",
            "Free marketing and content courses.",
            "https://academy.hubspot.com/"
        ),
        (
            "Coursera",
            "Online courses from universities and companies.",
            "https://www.coursera.org/"
        ),
        (
            "freeCodeCamp",
            "Free programming and development courses.",
            "https://www.freecodecamp.org/"
        ),
        (
            "W3Schools",
            "Learn web development and programming.",
            "https://www.w3schools.com/"
        ),
        (
            "YouTube Learning",
            "Explore tutorials and practical lessons.",
            "https://www.youtube.com/"
        ),
        (
            "Semrush Academy",
            "Learn SEO and digital marketing.",
            "https://www.semrush.com/academy/"
        )
    ]

    for title, description, url in resources:

        with st.container(border=True):
            st.subheader(title)
            st.write(description)
            st.markdown(f"[Visit Learning Platform]({url})")


# ==================================================
# PROGRESS TRACKING
# ==================================================

elif page == "Progress Tracking":

    st.title("📈 Learning Progress Tracking")

    roadmaps = get_all_roadmaps(current_user_id)

    if not roadmaps:
        st.info("Generate a roadmap to start tracking your progress.")

    else:
        roadmap_options = {
            f"{item['roadmap_title']} (ID: {item['roadmap_id']})":
            item["roadmap_id"]
            for item in roadmaps
        }

        selected_label = st.selectbox(
            "Select Roadmap",
            list(roadmap_options.keys())
        )

        roadmap_id = roadmap_options[selected_label]

        summary = get_progress_summary(roadmap_id, current_user_id)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Tasks", summary["total"])
        col2.metric("Completed", summary["completed"])
        col3.metric("Remaining", summary["remaining"])
        col4.metric("Progress", f"{summary['percentage']}%")

        st.subheader("Overall Progress")
        st.progress(summary["percentage"] / 100)

        tasks = get_tasks(roadmap_id, current_user_id)

        st.subheader("Task Checklist")

        if not tasks:
            st.info("No tasks available for this roadmap.")

        else:
            for task in tasks:

                task_id = task["task_id"]
                completed = bool(task.get("is_completed", 0))

                checked = st.checkbox(
                    f"Week {task['week_number']} — {task['topic']}",
                    value=completed,
                    key=f"task_{task_id}"
                )

                if checked != completed:
                    update_task_progress(task_id, current_user_id, checked)
                    st.rerun()

        st.subheader("Weekly Progress")

        weekly_data = {}

        for task in tasks:

            week = task["week_number"]

            if week not in weekly_data:
                weekly_data[week] = {
                    "total": 0,
                    "completed": 0
                }

            weekly_data[week]["total"] += 1

            if task.get("is_completed") == 1:
                weekly_data[week]["completed"] += 1

        for week, values in sorted(weekly_data.items()):

            total = values["total"]
            completed = values["completed"]

            percentage = completed / total if total else 0

            st.write(f"Week {week}: {completed}/{total} tasks")
            st.progress(percentage)


# ==================================================
# ADVANCED ANALYTICS DASHBOARD
# ==================================================

elif page == "Advanced Analytics":

    st.title("📊 Advanced Analytics Dashboard")

    st.write(
        "Analyze your learning performance, "
        "roadmap progress and task completion."
    )

    roadmaps = get_all_roadmaps(current_user_id)

    if not roadmaps:

        st.info("Create your first roadmap to view analytics.")

    else:

        total_roadmaps = len(roadmaps)
        total_tasks = 0
        completed_tasks = 0
        roadmap_performance = []

        for item in roadmaps:

            roadmap_id = item["roadmap_id"]
            tasks = get_tasks(roadmap_id, current_user_id)

            task_total = len(tasks)

            task_completed = sum(
                1 for task in tasks
                if task.get("is_completed") == 1
            )

            total_tasks += task_total
            completed_tasks += task_completed

            progress = (
                round(task_completed / task_total * 100, 1)
                if task_total else 0
            )

            roadmap_performance.append({
                "Roadmap": item.get(
                    "roadmap_title", "Learning Roadmap"
                ),
                "Career Goal": item.get("career_goal", ""),
                "Total Tasks": task_total,
                "Completed": task_completed,
                "Pending": task_total - task_completed,
                "Progress": f"{progress}%"
            })

        pending_tasks = total_tasks - completed_tasks

        overall_progress = (
            round(completed_tasks / total_tasks * 100, 1)
            if total_tasks else 0
        )

        # Performance Overview

        st.subheader("📌 Performance Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Roadmaps", total_roadmaps)
        col2.metric("Total Tasks", total_tasks)
        col3.metric("Completed Tasks", completed_tasks)
        col4.metric("Pending Tasks", pending_tasks)

        st.divider()

        # Overall Progress

        st.subheader("🎯 Overall Learning Progress")

        st.progress(overall_progress / 100)

        st.metric(
            "Overall Completion Rate",
            f"{overall_progress}%"
        )

        st.divider()

        # Task Distribution

        st.subheader("📈 Task Distribution")

        if total_tasks > 0:

            chart_data = {
                "Completed": [completed_tasks],
                "Pending": [pending_tasks]
            }

            st.bar_chart(chart_data)

            col1, col2 = st.columns(2)

            col1.metric("Completed Tasks", completed_tasks)
            col2.metric("Pending Tasks", pending_tasks)

        else:
            st.info("No tasks available for chart analysis.")

        st.divider()

        # Roadmap-wise Performance

        st.subheader("📚 Roadmap-wise Performance")

        st.table(roadmap_performance)

        st.divider()

        # Individual Roadmap Progress

        st.subheader("📊 Individual Roadmap Progress")

        for item in roadmap_performance:

            progress_value = float(
                item["Progress"].replace("%", "")
            )

            st.write(
                f"**{item['Roadmap']} — {item['Progress']}**"
            )

            st.progress(progress_value / 100)

        st.divider()

        # Learning Insights

        st.subheader("💡 Learning Insights")

        if overall_progress == 100 and total_tasks > 0:

            st.success(
                "Excellent! You have completed all your roadmap tasks."
            )

        elif overall_progress >= 50:

            st.success(
                "Great progress! Keep working towards your learning goals."
            )

        elif overall_progress > 0:

            st.info(
                "You have started your learning journey. "
                "Maintain consistency."
            )

        else:

            st.info(
                "Start completing your tasks to improve your progress."
            )

        st.caption(
            "Analytics are calculated from your saved roadmap tasks "
            "and progress records."
        )


# ==================================================
# BOTTOM PAGE NAVIGATION (RIGHT SIDE)
# ==================================================

current_page_index = PAGES.index(page)
st.divider()

# Keep the navigation controls aligned to the right side.
nav_space, previous_col, next_col = st.columns([6, 1.5, 1.5])

with previous_col:
    if current_page_index > 0:
        if st.button("← Previous", use_container_width=True, key="bottom_previous_button"):
            st.session_state["pending_page"] = PAGES[current_page_index - 1]
            st.rerun()

with next_col:
    if current_page_index < len(PAGES) - 1:
        if st.button("Next →", use_container_width=True, key="bottom_next_button"):
            st.session_state["pending_page"] = PAGES[current_page_index + 1]
            st.rerun()

st.caption(f"Page {current_page_index + 1} of {len(PAGES)}")


# ==================================================
# FOOTER
# ==================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "AI Skill Development Roadmap Generator"
)

st.sidebar.caption(
    "BCA Final Year Project"
)

st.sidebar.caption(
    "Learn. Practice. Achieve."
)
