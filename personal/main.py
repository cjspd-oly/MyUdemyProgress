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
  - Additional features: color-coded badges, lecture filters, favorite courses,
    lazy loading, auto-collapsing of completed sections, and a toggle to collapse/expand all.

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
PRELOAD_FILENAME = os.path.join(script_dir, "data/autosave.json")
SETTINGS_FILENAME = os.path.join(script_dir, "data/settings.json")
AUTOSAVE_FILENAME = os.path.join(script_dir, "data/autosave.json")

# ------------------------------------------------------------------------------
# Global Variables
# ------------------------------------------------------------------------------

# Universal status options for easier editing and filtering (emoji versions)
universal_status_options = [
    "❌ Not Done",
    "⏳ In Progress",
    "✅ Done",
    "⭐ Important",
    "⏰ Come Back Later",
    "⏭ Skip",
    "⏳ Maybe",
    "🚫 Ignore",
]

# Color mapping for statuses (for badges)
status_colors = {
    "❌ Not Done": "#e74c3c",
    "⏳ In Progress": "#f39c12",
    "✅ Done": "#27ae60",
    "⭐ Important": "#f1c40f",
    "⏭ Skip": "#7f8c8d",
    "⏳ Maybe": "#3498db",
    "🚫 Ignore": "#95a5a6",
}

# ------------------------------------------------------------------------------
# Settings Functions
# ------------------------------------------------------------------------------


def load_settings():
    """Load settings from the settings file."""
    if os.path.exists(SETTINGS_FILENAME):
        with open(SETTINGS_FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings):
    """Save settings to the settings file."""
    with open(SETTINGS_FILENAME, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def initialize_settings():
    """Initialize settings in session state if not already present."""
    if "settings" not in st.session_state:
        st.session_state["settings"] = load_settings()
    if "favorites" not in st.session_state["settings"]:
        st.session_state["settings"]["favorites"] = {}
    if "filter" not in st.session_state["settings"]:
        st.session_state["settings"]["filter"] = "All"
    if "preload" not in st.session_state["settings"]:
        st.session_state["settings"]["preload"] = True
    if "expand_all" not in st.session_state["settings"]:
        st.session_state["settings"]["expand_all"] = False
    if "autosave_setting" not in st.session_state["settings"]:
        st.session_state["settings"]["autosave_setting"] = False


# ------------------------------------------------------------------------------
# Helper: Convert loaded status to UI-compatible version
# ------------------------------------------------------------------------------


def get_ui_status(value):
    """
    Convert a loaded status value to a UI-compatible emoji-enhanced version.
    If the value is plain text (e.g. "Done"), map it using status_mapping.
    Comparison is case-insensitive and trims whitespace.
    """
    value_clean = value.strip().lower()
    for option in universal_status_options:
        if option.lower() == value_clean:
            return option
    mapping = {k.lower(): v for k, v in status_mapping.items()}
    if value_clean in mapping:
        return mapping[value_clean]
    return universal_status_options[0]


# ------------------------------------------------------------------------------
# Helper Functions (JSON, filenames, markdown)
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

status_mapping = {
    "Not Done": "❌ Not Done",
    "In Progress": "⏳ In Progress",
    "Done": "✅ Done",
    "Important": "⭐ Important",
    "Come Back Later": "⏰ Come Back Later",
    "Skip": "⏭ Skip",
    "Maybe": "⏳ Maybe",
    "Ignore": "🚫 Ignore",
}
reverse_mapping = {v: k for k, v in status_mapping.items()}


def get_plain_status(status):
    """Convert an emoji-enhanced status to plain text using our mapping."""
    return reverse_mapping.get(status, status)


def get_plain_statuses(statuses_dict):
    """Convert all statuses to plain text for saving."""
    return {k: get_plain_status(v) for k, v in statuses_dict.items()}


# ------------------------------------------------------------------------------
# Analytics Dashboard
# ------------------------------------------------------------------------------


def show_progress_dashboard(course_id, statuses):
    """
    Display a progress analytics dashboard for a selected course.
    """
    course_statuses = {
        k: v for k, v in statuses.items() if k.startswith(f"{course_id}-")
    }
    total = len(course_statuses)
    done = sum(1 for s in course_statuses.values() if s == "✅ Done")
    in_progress = sum(1 for s in course_statuses.values() if s == "⏳ In Progress")
    not_done = sum(1 for s in course_statuses.values() if s == "❌ Not Done")
    important = sum(1 for s in course_statuses.values() if s == "⭐ Important")
    come_back_later = sum(
        1 for s in course_statuses.values() if s == "⏰ Come Back Later"
    )
    maybe = sum(1 for s in course_statuses.values() if s == "⏳ Maybe")
    skip = sum(1 for s in course_statuses.values() if s == "⏭ Skip")
    ignore = sum(1 for s in course_statuses.values() if s == "🚫 Ignore")
    st.subheader("📊 Progress Analytics Dashboard")
    st.write(f"**Total Lectures:** {total}")
    st.write(
        f"✅ **Done:** {done} &nbsp;&nbsp; ⏳ **In Progress:** {in_progress} &nbsp;&nbsp; ❌ **Not Done:** {not_done}"
    )
    progress_percent = ((done+important) / (done + important + in_progress + skip + come_back_later + not_done) * 100) if total > 0 else 0
    st.progress(progress_percent / 100)
    st.write(f"**Completion:** {progress_percent:.1f}%")
    data = pd.DataFrame(
        {
            "Status": [
                "Done",
                "Not Done",
                "Important",
                "In Progress",
                "Come Back Later",
                "Skip",
                "Maybe",
                "Ignore",
            ],
            "Count": [
                done,
                not_done,
                important,
                in_progress,
                come_back_later,
                skip,
                maybe,
                ignore,
            ],
        }
    )
    st.bar_chart(data.set_index("Status"))


# ------------------------------------------------------------------------------
# Autosave Functions
# ------------------------------------------------------------------------------


def load_autosave():
    """
    Load autosaved data (if available) from autosave.json and convert loaded statuses
    to UI-compatible versions.
    """
    if os.path.exists(AUTOSAVE_FILENAME):
        try:
            data = load_json(AUTOSAVE_FILENAME)
            st.session_state["json_data"] = data.get("json_data")
            loaded_statuses = data.get("statuses", {})
            st.session_state["statuses"] = {
                k: get_ui_status(v) for k, v in loaded_statuses.items()
            }
            st.sidebar.info("Loaded autosave.json")
        except Exception as e:
            st.sidebar.error(f"Autosave error: {e}")


def save_autosave(json_data, statuses):
    """
    Save autosave data to autosave.json.
    Only plain text statuses are saved.
    """
    plain_statuses = get_plain_statuses(statuses)
    data = {"json_data": json_data, "statuses": plain_statuses}
    save_json(AUTOSAVE_FILENAME, data)


# ------------------------------------------------------------------------------
# Main App Functions
# ------------------------------------------------------------------------------


def initialize_session_state():
    """Initialize session state for JSON data, statuses, and settings."""
    if "json_data" not in st.session_state:
        st.session_state["json_data"] = None
    if "statuses" not in st.session_state:
        st.session_state["statuses"] = {}
    initialize_settings()


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
    """Render sidebar options for autosave, preload, course selection, filters, and expand all."""
    st.sidebar.header("⚙️ Options")
    autosave_setting = st.sidebar.checkbox(
        "💾 Autosave",
        value=st.session_state["settings"].get("autosave_setting", False),
        key="autosave_checkbox",
    )
    st.session_state["settings"]["autosave_setting"] = autosave_setting
    preload_enabled = st.sidebar.checkbox(
        "🚀 Preload JSON",
        value=st.session_state["settings"].get("preload", True),
        key="preload_checkbox",
    )
    universal_filter_options = ["All"] + universal_status_options
    filter_option = st.sidebar.selectbox(
        "Filter Lectures",
        universal_filter_options,
        index=universal_filter_options.index(
            st.session_state["settings"].get("filter", "All")
        ),
        key="lecture_filter",
    )
    st.session_state["settings"]["filter"] = filter_option
    expand_all = st.sidebar.checkbox(
        "Expand All Sections",
        value=st.session_state["settings"].get("expand_all", False),
        key="expand_all_checkbox",
    )
    st.session_state["settings"]["expand_all"] = expand_all
    if st.sidebar.button("💾 Save Settings", key="save_settings_button"):
        save_settings(st.session_state["settings"])
        st.sidebar.success("Settings saved!")
    return autosave_setting, preload_enabled, filter_option


def render_course_selection(json_data):
    """
    Build a course selection dropdown in the sidebar, sorting favorites to the top.
    Returns the selected course ID.
    """
    courses = []
    for cid, course in json_data.items():
        curr = course.get("curriculum_context", {}).get("data", {})
        title = curr.get("course_title", "Untitled")
        fav = st.session_state["settings"]["favorites"].get(cid, False)
        display = f"{'⭐ ' if fav else ''}{cid} - {title}"
        courses.append((cid, display))
    courses_sorted = sorted(
        courses,
        key=lambda x: (
            0 if st.session_state["settings"]["favorites"].get(x[0], False) else 1
        ),
    )
    options = [disp for cid, disp in courses_sorted]
    mapping = {disp: cid for cid, disp in courses_sorted}
    selected_course_option = st.sidebar.selectbox(
        "🎯 Select Course", options=options, key="course_select"
    )
    current_course = mapping[selected_course_option]
    fav_toggle = st.sidebar.checkbox(
        "⭐ Favorite",
        value=st.session_state["settings"]["favorites"].get(current_course, False),
        key="favorite_toggle",
    )
    st.session_state["settings"]["favorites"][current_course] = fav_toggle
    return mapping[selected_course_option]


def render_course_details(
    selected_course_id, json_data, statuses, status_options, filter_option
):
    """
    Render the main content for the selected course, including course summary,
    sections with individual status controls, master status updates, and section progress bars.
    Lecture items are filtered based on the sidebar filter.
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
    total_length = curriculum.get("estimated_content_length_text", "Unknown")
    st.markdown(
        f"**Content:** {total_secs} sections • {total_lecs} lectures • {total_length}"
    )
    expand_all = st.session_state["settings"].get("expand_all", False)
    for sec in curriculum.get("sections", []):
        sec_title = sec.get("title", "Untitled Section")
        length = sec.get("content_length_text", "Unknown")
        lect_count = sec.get("lecture_count", 0)
        done_count = sum(
            1
            for item in sec.get("items", [])
            if statuses.get(
                f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}",
                "❌ Not Done",
            )
            == "✅ Done"
        )
        section_header = (
            f"📂 {sec_title}  —  ✅ {done_count}/{lect_count} lectures • ⏱ {length}"
        )
        visible_items = []
        for item in sec.get("items", []):
            key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
            current_status = statuses.get(key, "❌ Not Done")
            if filter_option == "All" or current_status == filter_option:
                visible_items.append(item)
        # If filter is "All", use the "expand all" setting; else, expand if there is at least one visible item.
        if filter_option == "All":
            default_expanded = expand_all
        else:
            default_expanded = len(visible_items) > 0
        with st.expander(section_header, expanded=default_expanded):
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
            visible_count = 0
            for item in sec.get("items", []):
                key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{item.get('object_index', '0')}"
                current_status = statuses.get(key, "❌ Not Done")
                if filter_option != "All" and current_status != filter_option:
                    continue
                visible_count += 1
                badge_color = status_colors.get(current_status, "#000")
                lecture_badge = f"<span style='font-size:0.7em; color:white; background-color:{badge_color}; padding:1px 3px; border-radius:3px;'>{current_status}</span>"
                col1, col2, col3 = st.columns([6, 3, 3])
                with col1:
                    st.markdown(
                        f"{lecture_badge}<br><strong>{item.get('title', 'Untitled Item')}</strong>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"<p style='text-align:right'>{item.get('content_summary', 'Unknown')}</p>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    new_stat = st.selectbox(
                        "Status",
                        options=status_options,
                        index=(
                            status_options.index(current_status)
                            if current_status in status_options
                            else 0
                        ),
                        key=key + "_sel",
                    )
                    statuses[key] = new_stat
                st.markdown("---")
            if visible_count == 0:
                st.markdown("*No lectures match the selected filter.*")


def main():
    """Main function to run the Course TODO List Manager app."""
    initialize_session_state()
    autosave_setting, preload_enabled, filter_option = render_sidebar()

    # Preload autosave.json if it exists (contains json_data and statuses)
    if os.path.exists(AUTOSAVE_FILENAME):
        try:
            load_autosave()
            st.sidebar.success("Loaded autosave.json")
        except Exception as e:
            st.sidebar.error(f"Error loading autosave.json: {e}")
    # Otherwise, if preload is enabled, load from input.json
    elif (
        preload_enabled
        and os.path.exists(PRELOAD_FILENAME)
        and st.session_state["json_data"] is None
    ):
        try:
            st.session_state["json_data"] = load_json(PRELOAD_FILENAME)
            st.sidebar.success(f"Preloaded {PRELOAD_FILENAME}")
        except Exception as e:
            st.sidebar.error(f"Error preloading {PRELOAD_FILENAME}: {e}")

    handle_file_upload()

    if st.session_state["json_data"] is not None:
        # Merge statuses from the course JSON if available.
        for cid, course in st.session_state["json_data"].items():
            if "statuses" in course:
                for key, value in course["statuses"].items():
                    st.session_state["statuses"][key] = get_ui_status(value)
        json_data = st.session_state["json_data"]
        statuses = st.session_state["statuses"]
        status_options = universal_status_options
        selected_course_id = render_course_selection(json_data)
        dashboard_placeholder = st.empty()
        render_course_details(
            selected_course_id, json_data, statuses, status_options, filter_option
        )
        with dashboard_placeholder.container():
            show_progress_dashboard(selected_course_id, statuses)
        if autosave_setting:
            try:
                save_autosave(json_data, statuses)
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
        if st.sidebar.button("💾 Save All", key="save_all_button"):
            try:
                save_autosave(json_data, statuses)
                st.sidebar.success("Saved!")
            except Exception as e:
                st.sidebar.error(f"Save error: {e}")
    else:
        st.info("Please upload a JSON file or ensure autosave.json/input.json exists.")


# ------------------------------------------------------------------------------
# Custom CSS: Increase Scrollbar Width
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    ::-webkit-scrollbar {
      width: 16px;
    }
    ::-webkit-scrollbar-track {
      background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 6px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    main()
