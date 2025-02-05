# 3

import json
import os
import streamlit as st

AUTOSAVE_FILENAME = "autosave.json"
PRELOAD_FILENAME = "input.json"

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def generate_markdown(json_data, statuses):
    """Generate a Markdown representation of the course TODO list."""
    markdown = "# 📚 Course TODO List\n\n"
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown Instructor")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled Course")
        course_url = curriculum.get("course_url", "#")
        markdown += f"## [{course_title}]({course_url}) (👨‍🏫 {instructor})\n\n"
        for section in curriculum.get("sections", []):
            section_title = section.get("title", "Untitled Section")
            content_length = section.get("content_length_text", "Unknown Duration")
            lecture_count = section.get("lecture_count", 0)
            markdown += f"### 📂 {section_title} ({content_length}, {lecture_count} lectures)\n\n"
            markdown += "| 📝 Item (Title & Status) | ⏱ Duration | 🔗 Link |\n"
            markdown += "| --- | --- | --- |\n"
            for item in section.get("items", []):
                unique_key = f"{course_id}-{section_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                status = statuses.get(unique_key, "Not Done")
                item_title = item.get("title", "Untitled Item")
                # Combine title and status in one cell, with emojis for status if desired.
                item_cell = f"**{item_title}**<br>⚙️ Status: {status}"
                duration = item.get("content_summary", "Unknown Duration")
                learn_url = item.get("learn_url", "#")
                markdown += f"| {item_cell} | {duration} | [▶️ Learn]({learn_url}) |\n"
            markdown += "\n"
        markdown += "---\n\n"
    return markdown

# ==============================================
# Streamlit App: Course TODO List Manager
# ==============================================
st.title("📚 Course TODO List Manager")

# Sidebar options with emojis
st.sidebar.header("⚙️ Options")
autosave_enabled = st.sidebar.checkbox("💾 Autosave changes", value=False)
preload_enabled = st.sidebar.checkbox("🚀 Preload input.json", value=False)

# Option to preload file from code if selected
if preload_enabled and os.path.exists(PRELOAD_FILENAME) and st.session_state.get("json_data") is None:
    try:
        st.session_state["json_data"] = load_json(PRELOAD_FILENAME)
        st.sidebar.success(f"Preloaded data from {PRELOAD_FILENAME}")
    except Exception as e:
        st.sidebar.error(f"Error preloading {PRELOAD_FILENAME}: {e}")

# Initialize session state for JSON data and statuses if not already set
if "json_data" not in st.session_state:
    st.session_state["json_data"] = None
if "statuses" not in st.session_state:
    st.session_state["statuses"] = {}

# Load autosave.json if it exists and no JSON data is loaded yet
if st.session_state["json_data"] is None and os.path.exists(AUTOSAVE_FILENAME):
    try:
        autosave_data = load_json(AUTOSAVE_FILENAME)
        # Expecting autosave file to have "json_data" and "statuses"
        st.session_state["json_data"] = autosave_data.get("json_data")
        st.session_state["statuses"] = autosave_data.get("statuses", {})
        st.sidebar.info("Loaded data from autosave.json")
    except Exception as e:
        st.sidebar.error(f"Error loading autosave.json: {e}")

# Only show file uploader if no JSON data is loaded
if st.session_state["json_data"] is None:
    uploaded_file = st.file_uploader("📂 Upload JSON file", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state["json_data"] = json.load(uploaded_file)
            st.success("JSON file loaded successfully!")
        except Exception as e:
            st.error(f"Error reading JSON file: {e}")

# Proceed only if JSON data is loaded
if st.session_state["json_data"] is not None:
    json_data = st.session_state["json_data"]
    statuses = st.session_state["statuses"]
    status_options = ["Not Done", "In Progress", "Done", "Important", "Skip", "Ignore"]

    # Build a list of course IDs and titles for selection
    course_options = []
    course_id_title_map = {}
    for course_id, course in json_data.items():
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled Course")
        course_options.append(f"{course_id} - {course_title}")
        course_id_title_map[f"{course_id} - {course_title}"] = course_id

    selected_course_option = st.sidebar.selectbox("🎯 Select Course", options=course_options)
    selected_course_id = course_id_title_map[selected_course_option]

    # Display only the selected course
    course = json_data[selected_course_id]
    instructor = course.get("instructor", "Unknown Instructor")
    curriculum = course.get("curriculum_context", {}).get("data", {})
    course_title = curriculum.get("course_title", "Untitled Course")
    course_url = curriculum.get("course_url", "#")
    st.header(f"🔖 [{course_title}]({course_url}) (👨‍🏫 {instructor})")

    for section in curriculum.get("sections", []):
        section_title = section.get("title", "Untitled Section")
        content_length = section.get("content_length_text", "Unknown Duration")
        lecture_count = section.get("lecture_count", 0)
        st.subheader(f"📂 {section_title} ({content_length}, {lecture_count} lectures)")

        # Create a table-like layout for each item using columns
        for item in section.get("items", []):
            unique_key = f"{selected_course_id}-{section_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
            if unique_key not in statuses:
                statuses[unique_key] = "Not Done"

            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.markdown(f"**{item.get('title', 'Untitled Item')}**")
                st.markdown(f"⏱ Duration: {item.get('content_summary', 'Unknown Duration')}")
            with col2:
                new_status = st.selectbox(
                    f"Status for {item.get('title', 'Untitled Item')}",
                    options=status_options,
                    index=status_options.index(statuses[unique_key]),
                    key=unique_key + "_select"
                )
                statuses[unique_key] = new_status
            with col3:
                st.markdown(f"[▶️ Learn]({item.get('learn_url', '#')})")
            st.markdown("---")

    # Autosave functionality
    if autosave_enabled:
        try:
            autosave_data = {"json_data": json_data, "statuses": statuses}
            save_json(AUTOSAVE_FILENAME, autosave_data)
            st.sidebar.info(f"💾 Autosaved changes to {AUTOSAVE_FILENAME}")
        except Exception as e:
            st.sidebar.error(f"Autosave error: {e}")

    # Markdown download button in the sidebar
    markdown_output = generate_markdown({selected_course_id: course}, statuses)
    st.sidebar.download_button(
        label="📥 Download Markdown",
        data=markdown_output,
        file_name="output.md",
        mime="text/markdown"
    )
else:
    st.info("Please upload a JSON file or ensure autosave.json/input.json exists in the app directory.")
