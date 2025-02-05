# 1

import json
import os
import streamlit as st

AUTOSAVE_FILENAME = "autosave.json"


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def generate_markdown(json_data, statuses):
    """Generate a Markdown representation of the course TODO list."""
    markdown = "# Course TODO List\n\n"
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown Instructor")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled Course")
        course_url = curriculum.get("course_url", "#")
        markdown += f"## [{course_title}]({course_url}) (Instructor: {instructor})\n\n"
        for section in curriculum.get("sections", []):
            section_title = section.get("title", "Untitled Section")
            content_length = section.get("content_length_text", "Unknown Duration")
            lecture_count = section.get("lecture_count", 0)
            markdown += (
                f"### {section_title} ({content_length}, {lecture_count} lectures)\n\n"
            )
            markdown += "| Item (Title & Status) | Duration | Link |\n"
            markdown += "| --- | --- | --- |\n"
            for item in section.get("items", []):
                unique_key = f"{course_id}-{section_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                status = statuses.get(unique_key, "Not Done")
                item_title = item.get("title", "Untitled Item")
                # Combine title and status in one cell
                item_cell = f"**{item_title}**<br>Status: {status}"
                duration = item.get("content_summary", "Unknown Duration")
                learn_url = item.get("learn_url", "#")
                markdown += f"| {item_cell} | {duration} | [Learn]({learn_url}) |\n"
            markdown += "\n"
        markdown += "---\n\n"
    return markdown


# ==============================================
# Streamlit App: Course TODO List Manager
# ==============================================
st.title("Course TODO List Manager")

# Sidebar options
st.sidebar.header("Options")
autosave_enabled = st.sidebar.checkbox("Autosave changes", value=False)
export_markdown_clicked = st.sidebar.button("Export to Markdown")

# Initialize session state for JSON data and statuses
if "json_data" not in st.session_state:
    st.session_state["json_data"] = None
if "statuses" not in st.session_state:
    st.session_state["statuses"] = {}

# Load autosave.json if it exists and no data is loaded yet
if st.session_state["json_data"] is None and os.path.exists(AUTOSAVE_FILENAME):
    try:
        autosave_data = load_json(AUTOSAVE_FILENAME)
        # Expecting autosave file to have "json_data" and "statuses"
        st.session_state["json_data"] = autosave_data.get("json_data")
        st.session_state["statuses"] = autosave_data.get("statuses", {})
        st.info("Loaded data from autosave.json.")
    except Exception as e:
        st.error(f"Error loading autosave.json: {e}")

# Only show file uploader if no JSON data is loaded
if st.session_state["json_data"] is None:
    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state["json_data"] = json.load(uploaded_file)
            st.success("JSON file loaded successfully!")
        except Exception as e:
            st.error(f"Error reading JSON file: {e}")

# Only proceed if JSON data is loaded
if st.session_state["json_data"] is not None:
    json_data = st.session_state["json_data"]
    statuses = st.session_state["statuses"]
    status_options = ["Not Done", "In Progress", "Done", "Important", "Skip", "Ignore"]

    # Iterate through courses and their sections
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown Instructor")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled Course")
        course_url = curriculum.get("course_url", "#")
        st.header(f"[{course_title}]({course_url}) (Instructor: {instructor})")

        for section in curriculum.get("sections", []):
            section_title = section.get("title", "Untitled Section")
            content_length = section.get("content_length_text", "Unknown Duration")
            lecture_count = section.get("lecture_count", 0)
            st.subheader(
                f"{section_title} ({content_length}, {lecture_count} lectures)"
            )

            # Create a table-like layout for each item using columns
            for item in section.get("items", []):
                # Create a unique key for each item using course_id, section title, item title, and object_index if available
                unique_key = f"{course_id}-{section_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                if unique_key not in statuses:
                    statuses[unique_key] = "Not Done"

                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    st.markdown(f"**{item.get('title', 'Untitled Item')}**")
                    st.markdown(
                        f"Duration: {item.get('content_summary', 'Unknown Duration')}"
                    )
                with col2:
                    # Unique key used for selectbox to avoid duplicates
                    new_status = st.selectbox(
                        f"Status for {item.get('title', 'Untitled Item')}",
                        options=status_options,
                        index=status_options.index(statuses[unique_key]),
                        key=unique_key + "_select",
                    )
                    statuses[unique_key] = new_status
                with col3:
                    st.markdown(f"[Learn]({item.get('learn_url', '#')})")
                st.markdown("---")

    # Autosave functionality
    if autosave_enabled:
        try:
            autosave_data = {"json_data": json_data, "statuses": statuses}
            save_json(AUTOSAVE_FILENAME, autosave_data)
            st.info(f"Autosaved changes to {AUTOSAVE_FILENAME}")
        except Exception as e:
            st.error(f"Autosave error: {e}")

    # Export to Markdown on button click
    if export_markdown_clicked:
        markdown_output = generate_markdown(json_data, statuses)
        st.download_button(
            label="Download Markdown",
            data=markdown_output,
            file_name="output.md",
            mime="text/markdown",
        )
else:
    st.info(
        "Please upload a JSON file or place an autosave.json file in the app directory."
    )
