import json
import os
import io
import zipfile
import re
import streamlit as st

AUTOSAVE_FILENAME = "data/autosave.json"
PRELOAD_FILENAME = "data/input.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def sanitize_filename(filename):
    # Remove characters that are not allowed in Windows filenames and most OSes
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def generate_markdown(json_data, statuses):
    """Generate a Markdown representation of the course TODO list for all courses."""
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
                item_cell = f"**{item_title}**<br>⚙️ Status: {status}"
                duration = item.get("content_summary", "Unknown Duration")
                learn_url = item.get("learn_url", "#")
                markdown += f"| {item_cell} | {duration} | [▶️ Learn]({learn_url}) |\n"
            markdown += "\n"
        markdown += "---\n\n"
    return markdown


def generate_individual_markdowns(json_data, statuses):
    """Generate a dictionary of filename: markdown for individual courses."""
    md_files = {}
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown Instructor")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled Course")
        course_url = curriculum.get("course_url", "#")
        # Build a filename: {course_id} - {course_title}.md and sanitize it.
        file_name = sanitize_filename(f"{course_id} - {course_title}.md")
        markdown = f"# 📚 {course_title} (👨‍🏫 {instructor})\n\n"
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
                item_cell = f"**{item_title}**<br>⚙️ Status: {status}"
                duration = item.get("content_summary", "Unknown Duration")
                learn_url = item.get("learn_url", "#")
                markdown += f"| {item_cell} | {duration} | [▶️ Learn]({learn_url}) |\n"
            markdown += "\n"
        md_files[file_name] = markdown
    return md_files


# ==============================================
# Streamlit App: Course TODO List Manager
# ==============================================
st.title("📚 Course TODO List Manager")

# Sidebar options with emojis
st.sidebar.header("⚙️ Options")
autosave_enabled = st.sidebar.checkbox("💾 Autosave changes", value=False)
preload_enabled = st.sidebar.checkbox("🚀 Preload input.json", value=False)

# Option to preload file from code if selected
if (
    preload_enabled
    and os.path.exists(PRELOAD_FILENAME)
    and st.session_state.get("json_data") is None
):
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
        display_text = f"{course_id} - {course_title}"
        course_options.append(display_text)
        course_id_title_map[display_text] = course_id

    selected_course_option = st.sidebar.selectbox(
        "🎯 Select Course", options=course_options
    )
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
                st.markdown(
                    f"⏱ Duration: {item.get('content_summary', 'Unknown Duration')}"
                )
            with col2:
                new_status = st.selectbox(
                    f"Status for {item.get('title', 'Untitled Item')}",
                    options=status_options,
                    index=status_options.index(statuses[unique_key]),
                    key=unique_key + "_select",
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

    # Markdown download button for the selected course (individual)
    selected_course_md = generate_markdown({selected_course_id: course}, statuses)
    # Generate a filename for the selected course
    selected_filename = sanitize_filename(
        f"{selected_course_id} - {curriculum.get('course_title', 'Untitled Course')}.md"
    )
    st.sidebar.download_button(
        label="📥 Download Selected Course Markdown",
        data=selected_course_md,
        file_name=selected_filename,
        mime="text/markdown",
    )

    # Download combined markdown for all courses
    combined_md = generate_markdown(json_data, statuses)
    st.sidebar.download_button(
        label="📥 Download Combined Markdown (All Courses)",
        data=combined_md,
        file_name="All Courses - Combined Markdown.md",
        mime="text/markdown",
    )

    # Generate individual markdown files and package them in a ZIP archive
    md_files = generate_individual_markdowns(json_data, statuses)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_name, markdown_text in md_files.items():
            zip_file.writestr(file_name, markdown_text)
    zip_buffer.seek(0)
    st.sidebar.download_button(
        label="📥 Download Individual Markdown Files (ZIP)",
        data=zip_buffer,
        file_name="Individual_Markdowns.zip",
        mime="application/zip",
    )

    # Final save button to save data for all courses
    if st.sidebar.button("💾 Save All Changes"):
        try:
            all_data = {"json_data": json_data, "statuses": statuses}
            save_json(AUTOSAVE_FILENAME, all_data)
            st.sidebar.success(f"All changes saved to {AUTOSAVE_FILENAME}!")
        except Exception as e:
            st.sidebar.error(f"Final save error: {e}")
else:
    st.info(
        "Please upload a JSON file or ensure autosave.json/input.json exists in the app directory."
    )
