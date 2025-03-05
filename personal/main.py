"""
Course TODO List Manager
========================

This Streamlit app helps manage course progress by displaying course details,
sections, lectures, and progress analytics. It supports:
  - Preloading JSON data from a local file.
  - Autosaving changes.
  - Displaying courses with collapsible sections.
  - Master status updates per section.
  - Emoji-enhanced status display in the UI while saving plain statuses in JSON.
  - Exporting course details as Markdown files and a ZIP archive.
  - A progress analytics dashboard that always appears at the top.

To run:
    streamlit run main.py

Author: Your Name
Date: YYYY-MM-DD
"""

import json
import os
import io
import zipfile
import re
import streamlit as st
import pandas as pd  # For analytics charts

# 🛠️ Fix: file path
script_dir = os.path.dirname(os.path.abspath(__file__))


# Constants for file paths
AUTOSAVE_FILENAME = os.path.join(script_dir, "data/autosave.json")
PRELOAD_FILENAME = os.path.join(script_dir, "data/input.json")

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------


def load_json(file_path):
    """Load and return JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    """Save data as JSON to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def sanitize_filename(filename):
    """Sanitize a string to be a valid filename."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def generate_markdown(json_data, statuses):
    """Generate a Markdown representation for all courses."""
    md = "# 📚 Course TODO List\n\n"
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled")
        course_url = curriculum.get("course_url", "#")
        md += f"## [{course_title}]({course_url}) (👨‍🏫 {instructor})\n\n"
        for section in curriculum.get("sections", []):
            sec_title = section.get("title", "Untitled Section")
            length = section.get("content_length_text", "Unknown")
            lect_count = section.get("lecture_count", 0)
            md += f"### 📂 {sec_title} ({length}, {lect_count} lectures)\n\n"
            md += "| 📝 Item (Title & Status) | ⏱ Duration | 🔗 Link |\n| --- | --- | --- |\n"
            for item in section.get("items", []):
                key = f"{course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                status = statuses.get(key, "❌ Not Done")
                title = item.get("title", "Untitled Item")
                cell = f"**{title}**<br>⚙️ {status}"
                duration = item.get("content_summary", "Unknown")
                learn_url = item.get("learn_url", "#")
                md += f"| {cell} | {duration} | [▶️ Learn]({learn_url}) |\n"
            md += "\n"
        md += "---\n\n"
    return md


def generate_individual_markdowns(json_data, statuses):
    """
    Generate individual Markdown files for each course.

    Returns a dictionary with filenames as keys and Markdown text as values.
    """
    files = {}
    for course_id, course in json_data.items():
        instructor = course.get("instructor", "Unknown")
        curriculum = course.get("curriculum_context", {}).get("data", {})
        course_title = curriculum.get("course_title", "Untitled")
        course_url = curriculum.get("course_url", "#")
        fname = sanitize_filename(f"{course_id} - {course_title}.md")
        md = f"# 📚 {course_title} (👨‍🏫 {instructor})\n\n"
        for section in curriculum.get("sections", []):
            sec_title = section.get("title", "Untitled Section")
            length = section.get("content_length_text", "Unknown")
            lect_count = section.get("lecture_count", 0)
            md += f"### 📂 {sec_title} ({length}, {lect_count} lectures)\n\n"
            md += "| 📝 Item (Title & Status) | ⏱ Duration | 🔗 Link |\n| --- | --- | --- |\n"
            for item in section.get("items", []):
                key = f"{course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                status = statuses.get(key, "❌ Not Done")
                title = item.get("title", "Untitled Item")
                cell = f"**{title}**<br>⚙️ {status}"
                duration = item.get("content_summary", "Unknown")
                learn_url = item.get("learn_url", "#")
                md += f"| {cell} | {duration} | [▶️ Learn]({learn_url}) |\n"
            md += "\n"
        files[fname] = md
    return files


# ------------------------------------------------------------------------------
# Status Mapping (Plain <-> Emoji)
# ------------------------------------------------------------------------------

# Mapping for converting plain statuses to emoji-enhanced versions (used in the UI)
status_mapping = {
    "Not Done": "❌ Not Done",
    "In Progress": "⏳ In Progress",
    "Done": "✅ Done",
    "Important": "⭐ Important",
    "Skip": "⏭ Skip",
    "Maybe": "⏳ Maybe",
    "Ignore": "🚫 Ignore",
}
# Reverse mapping to convert emoji statuses back to plain text for saving
reverse_mapping = {v: k for k, v in status_mapping.items()}

# ------------------------------------------------------------------------------
# Analytics Dashboard
# ------------------------------------------------------------------------------


def show_progress_dashboard(course_id, statuses):
    """
    Display a progress analytics dashboard for a selected course.
    """
    # Filter statuses to include only those for the current course.
    course_statuses = {
        k: v for k, v in statuses.items() if k.startswith(f"{course_id}-")
    }
    total = len(course_statuses)
    done = sum(1 for s in course_statuses.values() if s == "✅ Done")
    in_progress = sum(1 for s in course_statuses.values() if s == "⏳ In Progress")
    not_done = sum(1 for s in course_statuses.values() if s == "❌ Not Done")
    important = sum(1 for s in course_statuses.values() if s == "⭐ Important")
    maybe = sum(1 for s in course_statuses.values() if s == "⏳ Maybe")
    skip = sum(1 for s in course_statuses.values() if s == "⏭ Skip")
    ignore = sum(1 for s in course_statuses.values() if s == "🚫 Ignore")

    st.subheader("📊 Progress Analytics Dashboard")
    st.write(f"**Total Lectures:** {total}")
    st.write(
        f"✅ **Done:** {done} &nbsp;&nbsp; ⏳ **In Progress:** {in_progress} &nbsp;&nbsp; ❌ **Not Done:** {not_done}"
    )
    progress_percent = (done / (done + not_done) * 100) if total > 0 else 0
    st.progress(progress_percent / 100)
    st.write(f"**Completion:** {progress_percent:.3f}%")

    data = pd.DataFrame(
        {
            "Status": [
                "Done",
                "Not Done",
                "Important",
                "In Progress",
                "Skip",
                "Maybe",
                "Ignore",
            ],
            "Count": [done, not_done, important, in_progress, skip, maybe, ignore],
        }
    )
    st.bar_chart(data.set_index("Status"))


# ------------------------------------------------------------------------------
# Main App Functions
# ------------------------------------------------------------------------------


def initialize_session_state():
    """Initialize session state for JSON data and statuses if they do not exist."""
    if "json_data" not in st.session_state:
        st.session_state["json_data"] = None
    if "statuses" not in st.session_state:
        st.session_state["statuses"] = {}


def load_autosave():
    """
    Load autosaved data (if available) and convert plain statuses to emoji-enhanced versions.
    """
    if os.path.exists(AUTOSAVE_FILENAME):
        try:
            data = load_json(AUTOSAVE_FILENAME)
            st.session_state["json_data"] = data.get("json_data")
            loaded_statuses = data.get("statuses", {})
            st.session_state["statuses"] = {
                k: status_mapping.get(v, v) for k, v in loaded_statuses.items()
            }
            st.sidebar.info("Loaded autosave")
        except Exception as e:
            st.sidebar.error(f"Autosave error: {e}")


def handle_file_upload():
    """Display a file uploader to load JSON data if none is available."""
    if st.session_state["json_data"] is None:
        uploaded_file = st.file_uploader("📂 Upload JSON", type=["json"])
        if uploaded_file is not None:
            try:
                st.session_state["json_data"] = json.load(uploaded_file)
                st.success("JSON loaded!")
            except Exception as e:
                st.error(f"Error reading JSON: {e}")


def render_sidebar():
    """Render the sidebar options for autosave, preload, and course selection."""
    st.sidebar.header("⚙️ Options")
    autosave_enabled = st.sidebar.checkbox("💾 Autosave", value=False)
    preload_enabled = st.sidebar.checkbox("🚀 Preload JSON", value=False)
    return autosave_enabled, preload_enabled


def render_course_selection(json_data):
    """
    Build a course selection dropdown in the sidebar.

    Returns the selected course ID.
    """
    course_options = []
    course_id_title_map = {}
    for cid, course in json_data.items():
        curr = course.get("curriculum_context", {}).get("data", {})
        title = curr.get("course_title", "Untitled")
        disp = f"{cid} - {title}"
        course_options.append(disp)
        course_id_title_map[disp] = cid

    selected_course_option = st.sidebar.selectbox(
        "🎯 Select Course", options=course_options
    )
    return course_id_title_map[selected_course_option]


def render_course_details(selected_course_id, json_data, statuses, status_options):
    """
    Render the main content for the selected course, including course summary,
    sections with individual status controls, and master status updates.
    """
    course = json_data[selected_course_id]
    instructor = course.get("instructor", "Unknown")
    curriculum = course.get("curriculum_context", {}).get("data", {})
    course_title = curriculum.get("course_title", "Untitled")
    course_url = curriculum.get("course_url", "#")
    st.header(f"🔖 [{course_title}]({course_url}) (👨‍🏫 {instructor})")

    total_secs = len(curriculum.get("sections", []))
    total_lecs = sum(
        sec.get("lecture_count", 0) for sec in curriculum.get("sections", [])
    )
    # Use 'estimated_content_length_text' for the course's total length
    total_length = curriculum.get("estimated_content_length_text", "Unknown")
    st.markdown(
        f"**Content:** {total_secs} sections • {total_lecs} lectures • {total_length}"
    )

    # Render each section with master status and individual lecture controls.
    for sec in curriculum.get("sections", []):
        sec_title = sec.get("title", "Untitled Section")
        length = sec.get("content_length_text", "Unknown")
        lect_count = sec.get("lecture_count", 0)
        exp_label = f"📂 {sec_title} ({lect_count} lec • {length})"
        with st.expander(exp_label, expanded=False):
            master_key = f"master-{selected_course_id}-{sec_title}"
            col_m1, col_m2 = st.columns([8, 2])
            with col_m1:
                master_status = st.selectbox(
                    "🎛️ Master Status", options=["---"] + status_options, key=master_key
                )
            with col_m2:
                if st.button("✅ Apply", key=master_key + "_apply"):
                    for item in sec.get("items", []):
                        if master_status == "---":
                            continue
                        key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                        statuses[key] = master_status
            st.markdown("---")
            # Render individual lecture items.
            for item in sec.get("items", []):
                key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                if key not in statuses:
                    statuses[key] = "❌ Not Done"
                elif statuses[key] not in status_options:
                    statuses[key] = status_mapping.get(statuses[key], "❌ Not Done")

                col1, col2, col3 = st.columns([6, 3, 3])
                with col1:
                    st.markdown(f"**{item.get('title', 'Untitled Item')}**")
                with col2:
                    st.markdown(
                        f"<p style='text-align:right'>{item.get('content_summary', 'Unknown')}</p>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    new_stat = st.selectbox(
                        "Status",
                        options=status_options,
                        index=status_options.index(statuses[key]),
                        key=key + "_sel",
                    )
                    statuses[key] = new_stat
                st.markdown("---")


def main():
    """Main function to run the Course TODO List Manager app."""
    # Render sidebar options
    autosave_enabled, preload_enabled = render_sidebar()
    initialize_session_state()

    # Preload JSON if enabled and no data is loaded yet.
    if (
        preload_enabled
        and os.path.exists(PRELOAD_FILENAME)
        and st.session_state["json_data"] is None
    ):
        try:
            st.session_state["json_data"] = load_json(PRELOAD_FILENAME)
            st.sidebar.success(f"Preloaded {PRELOAD_FILENAME}")
        except Exception as e:
            st.sidebar.error(f"Error preloading: {e}")

    # Load autosave data if available and data is not yet loaded.
    if st.session_state["json_data"] is None:
        load_autosave()

    # Handle file upload if no data is available.
    handle_file_upload()

    # Proceed if JSON data is available.
    if st.session_state["json_data"] is not None:
        json_data = st.session_state["json_data"]
        statuses = st.session_state["statuses"]
        # Emoji-enhanced status options for the UI.
        status_options = [
            "❌ Not Done",
            "⏳ In Progress",
            "✅ Done",
            "⭐ Important",
            "⏭ Skip",
            "⏳ Maybe",
            "🚫 Ignore",
        ]

        # Render course selection and get selected course ID.
        selected_course_id = render_course_selection(json_data)

        # Create a dashboard placeholder immediately after course selection so that
        # the progress dashboard always appears at the top.
        dashboard_placeholder = st.empty()

        # Render detailed view for the selected course (course details appear below).
        render_course_details(selected_course_id, json_data, statuses, status_options)

        # Update the dashboard placeholder with the latest progress analytics.
        with dashboard_placeholder.container():
            show_progress_dashboard(selected_course_id, statuses)

        # --------------------------
        # Save and Export Functionality
        # --------------------------
        def get_plain_statuses(statuses_dict):
            """Convert emoji-enhanced statuses to plain text for saving."""
            return {k: reverse_mapping.get(v, v) for k, v in statuses_dict.items()}

        if autosave_enabled:
            try:
                plain_statuses = get_plain_statuses(statuses)
                save_json(
                    AUTOSAVE_FILENAME,
                    {"json_data": json_data, "statuses": plain_statuses},
                )
                st.sidebar.info("💾 Autosaved")
            except Exception as e:
                st.sidebar.error(f"Autosave error: {e}")

        sel_md = generate_markdown(
            {selected_course_id: json_data[selected_course_id]}, statuses
        )
        sel_fname = sanitize_filename(
            f"{selected_course_id} - {json_data[selected_course_id].get('curriculum_context', {}).get('data', {}).get('course_title', 'Untitled')}.md"
        )
        st.sidebar.download_button(
            "📥 Download Course MD",
            data=sel_md,
            file_name=sel_fname,
            mime="text/markdown",
        )

        comb_md = generate_markdown(json_data, statuses)
        st.sidebar.download_button(
            "📥 Download All MD",
            data=comb_md,
            file_name="All Courses - Combined Markdown.md",
            mime="text/markdown",
        )

        md_files = generate_individual_markdowns(json_data, statuses)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for fname, mdtxt in md_files.items():
                zip_file.writestr(fname, mdtxt)
        zip_buffer.seek(0)
        st.sidebar.download_button(
            "📥 Download MD ZIP",
            data=zip_buffer,
            file_name="Individual_Markdowns.zip",
            mime="application/zip",
        )

        if st.sidebar.button("💾 Save All"):
            try:
                plain_statuses = get_plain_statuses(statuses)
                save_json(
                    AUTOSAVE_FILENAME,
                    {"json_data": json_data, "statuses": plain_statuses},
                )
                st.sidebar.success("Saved!")
            except Exception as e:
                st.sidebar.error(f"Save error: {e}")
    else:
        st.info("Please upload a JSON file or ensure autosave.json/input.json exists.")


if __name__ == "__main__":
    main()
