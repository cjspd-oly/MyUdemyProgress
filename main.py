"""
MyUdemyProgress
========================

This is a Streamlit-based web application that helps you track your progress across online courses. It offers a modern, interactive interface to monitor course details, update lecture statuses, and view comprehensive progress analytics—all while seamlessly saving and loading your progress.

- **Preload & Autosave:**
    Automatically load your progress from a local JSON file (`autosave.json`) and manually save changes to preserve your updates across sessions.
- **Course & Section Display:**
    View complete course details with collapsible sections that show lectures and their statuses. The app automatically saves and loads the selected course, ensuring you can resume exactly where you left off.
- **Master Status Updates:**
    Quickly update the status of all lectures within a section using intuitive master controls.
- **Emoji-Enhanced Statuses:**
    Enjoy vivid, emoji-enhanced status badges for better visual distinction while the app saves plain text statuses to maintain compatibility with older data formats.
- **Export Options:**
    Generate Markdown reports for individual courses or combine multiple courses into one file. Download all reports in a ZIP archive for offline use.
- **Progress Analytics Dashboard:**
    See detailed, real-time analytics—including completion percentages and status breakdowns—to track your course progress at a glance.
- **Additional Features:**
    - **Lecture Filtering & Favorites:** Easily filter lectures by status and mark courses as favorites for quick access.
    - **Optimized UI:** Experience a responsive, lazy-loaded interface with an enhanced scrollbar and auto-collapsing sections for a streamlined workflow.

To run:
    streamlit run main.py
"""

import json
import os
import io
import zipfile
import re
import streamlit as st
import pandas as pd  # For analytics charts

# --- File Paths Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
PRELOAD_FILENAME = os.path.join(script_dir, "data/autosave.json")
SETTINGS_FILENAME = os.path.join(script_dir, "data/settings.json")
AUTOSAVE_FILENAME = os.path.join(script_dir, "data/autosave.json")

# --- Global Variables & Mappings ---
# ? Done: Done
# ? Not Done: Not Done (TODO / One after another)
# ? In Progress: Currently going on
# ? Important: Done & Important
# ? Ignore: Ignore without seeing (no need)
# ? Come Back Later: Skip but come back ASAP
# ? SKip: Skip with no definite time limit + if time permits
# ? Maybe: Not Decided yet + Most probably to be ignore or maybe skip

# TODO: Use status_info directly, remove derived vars; skipping due to too many changes.
# TODO: status_info need to be unified with show_progress_dashboard()
# --- Unified Status Information ---
status_info = {
    "Not Done": {"display": "❌ Not Done", "color": "#e74c3c"},
    "In Progress": {"display": "⏳ In Progress", "color": "#f39c12"},
    "Done": {"display": "✅ Done", "color": "#27ae60"},
    "Important": {"display": "⭐ Important", "color": "#f1c40f"},
    "Come Back Later": {"display": "⏰ Come Back Later", "color": "#f1c40f"},
    "Skip": {"display": "⏭ Skip", "color": "#7f8c8d"},
    "Maybe": {"display": "⏳ Maybe", "color": "#3498db"},
    "Ignore": {"display": "🚫 Ignore", "color": "#95a5a6"},
}

# Derived variables:
universal_status_options = [info["display"] for info in status_info.values()]
status_mapping = {status: info["display"] for status, info in status_info.items()}
reverse_mapping = {info["display"]: status for status, info in status_info.items()}
status_colors = {info["display"]: info["color"] for _, info in status_info.items()}


# --- JSON I/O Helpers ---
def load_json(file_path):
    """Load settings from the settings file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.sidebar.error(f"Error loading {file_path}: {e}")
        return {}


def save_json(file_path, data):
    """Save settings to the settings file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error saving to {file_path}: {e}")


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)


# --- Settings Functions ---
def load_settings():
    """Load settings from the settings file."""
    return load_json(SETTINGS_FILENAME)


def save_settings(settings):
    """Save settings to the settings file."""
    save_json(SETTINGS_FILENAME, settings)


def initialize_settings():
    """Initialize settings in session state if not already present."""
    if "settings" not in st.session_state:
        st.session_state["settings"] = load_settings()
    st.session_state["settings"].setdefault("favorites", {})
    st.session_state["settings"].setdefault("preload", True)
    st.session_state["settings"].setdefault("autosave_setting", False)
    st.session_state["settings"].setdefault("filter", "All")
    st.session_state["settings"].setdefault("selected_course", None)


# --- Session State Initialization ---
def initialize_session_state():
    """Initialize session state for JSON data, statuses, and settings."""
    if "json_data" not in st.session_state:
        st.session_state["json_data"] = None
    if "statuses" not in st.session_state:
        st.session_state["statuses"] = {}
    initialize_settings()


# --- Status Conversion Helpers ---
def get_ui_status(value):
    """
    Convert a loaded status value to a UI-compatible emoji-enhanced version.
    If the value is plain text (e.g. "Done"), map it using status_mapping.
    Comparison is case-insensitive and trims whitespace.
    """
    try:
        value_clean = value.strip().lower()
    except AttributeError:
        value_clean = ""
    for option in universal_status_options:
        if option.lower() == value_clean:
            return option
    mapping = {k.lower(): v for k, v in status_mapping.items()}
    return mapping.get(value_clean, universal_status_options[0])


def get_plain_status(status):
    """Convert an emoji-enhanced status to plain text using our mapping."""
    return reverse_mapping.get(status, status)


def get_plain_statuses(statuses_dict):
    """Convert all statuses to plain text for saving."""
    return {k: get_plain_status(v) for k, v in statuses_dict.items()}


# --- Autosave Functions ---
def load_autosave():
    """
    Load autosaved data (if available) from autosave.json and convert loaded statuses
    to UI-compatible versions.
    """
    if os.path.exists(AUTOSAVE_FILENAME):
        try:
            data = load_json(AUTOSAVE_FILENAME)
            st.session_state["json_data"] = data.get("json_data", {})
            loaded_statuses = data.get("statuses", {})
            st.session_state["statuses"] = {
                k: get_ui_status(v) for k, v in loaded_statuses.items()
            }
            st.sidebar.info("Loaded autosave.json")
        except Exception as e:
            st.sidebar.error(f"Autosave error: {e}")


def save_autosave():
    """
    Save autosave data to autosave.json.
    Only plain text statuses are saved.
    """
    plain_statuses = get_plain_statuses(st.session_state["statuses"])
    data = {"json_data": st.session_state["json_data"], "statuses": plain_statuses}
    save_json(AUTOSAVE_FILENAME, data)


# --- File Upload ---
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


# --- Export: Markdown ---
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


# --- Sidebar Rendering ---
def render_sidebar():
    """Render sidebar options for autosave, preload, course selection, filters"""
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
    st.session_state["settings"]["preload"] = preload_enabled

    filter_option = st.sidebar.selectbox(
        "🔍 Filter Lectures",
        ["All"] + universal_status_options,
        index=(
            0
            if st.session_state["settings"].get("filter", "All") == "All"
            else universal_status_options.index(
                st.session_state["settings"].get("filter", "All")
            )
        ),
        key="lecture_filter",
    )
    st.session_state["settings"]["filter"] = filter_option

    if st.sidebar.button("💾 Save Settings", key="save_settings_button"):
        save_settings(st.session_state["settings"])
        st.sidebar.success("Settings saved!")
    if st.sidebar.button("💾 Save All", key="save_all_button"):
        try:
            save_autosave()
            st.sidebar.success("Progress saved to autosave.json")
        except Exception as e:
            st.sidebar.error(f"Autosave error: {e}")
    return autosave_setting, preload_enabled, filter_option


# --- Course Selection ---
def render_course_selection(json_data):
    """
    Builds the course selection dropdown in the sidebar, with favorites pinned at the top.
    Remembers and restores the last selected course across sessions.
    Returns the selected course ID.
    """
    courses = []
    for cid, course in json_data.items():
        try:
            title = course["curriculum_context"]["data"].get("course_title", "Untitled")
        except Exception:
            title = "Untitled"
        fav = st.session_state["settings"]["favorites"].get(cid, False)
        display = f"{'⭐ ' if fav else ''}{cid} - {title}"
        courses.append((cid, display))

    courses_sorted = sorted(
        courses,
        key=lambda x: (
            0 if st.session_state["settings"]["favorites"].get(x[0], False) else 1
        ),
    )

    options = [disp for _, disp in courses_sorted]
    mapping = {disp: cid for cid, disp in courses_sorted}

    default_course = st.session_state["settings"].get("selected_course", None)
    default_index = 0
    if default_course:
        for disp, cid in mapping.items():
            if cid == default_course and disp in options:
                default_index = options.index(disp)
                break

    selected_option = st.sidebar.selectbox(
        "🎯 Select Course", options, index=default_index, key="course_select"
    )
    current_course = mapping[selected_option]

    # ✅ Save selected course only if changed
    if st.session_state["settings"].get("selected_course") != current_course:
        st.session_state["settings"]["selected_course"] = current_course
        save_settings(st.session_state["settings"])

    fav_toggle = st.sidebar.checkbox(
        "⭐ Favorite",
        value=st.session_state["settings"]["favorites"].get(current_course, False),
        key="favorite_toggle",
    )
    st.session_state["settings"]["favorites"][current_course] = fav_toggle

    return current_course


# --- Course Details Rendering ---
def render_course_details(
    selected_course_id, json_data, statuses, status_options, filter_option
):
    """
    Render the main content for the selected course, including course summary,
    sections with individual status controls, master status updates, and section progress bars.
    Lecture items are filtered based on the sidebar filter.
    """
    try:
        course = json_data[selected_course_id]
        curriculum = course["curriculum_context"]["data"]
    except Exception:
        st.error("Error: Invalid course data structure.")
        return
    instructor = course.get("instructor", "Unknown")
    st.header(
        f"🔖 [{curriculum.get('course_title', 'Untitled')}]({curriculum.get('course_url', '#')}) (👨‍🏫 {instructor})"
    )
    st.markdown(
        f"**Content:** {len(curriculum.get('sections', []))} sections • {curriculum.get('num_of_published_lectures', 0)} lectures • {curriculum.get('estimated_content_length_text', 'Unknown')}"
    )
    for section in curriculum.get("sections", []):
        sec_title = section.get("title", "Untitled Section")
        length = section.get("content_length_text", "Unknown")
        lect_count = section.get("lecture_count", 0)
        done_count = sum(
            1
            for idx, item in enumerate(section.get("items", []))
            if statuses.get(
                f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{str(item.get('object_index', idx))}",
                "❌ Not Done",
            )
            == "✅ Done"
        )
        section_header = (
            f"📂 {sec_title} — ✅ {done_count}/{lect_count} lectures • ⏱ {length}"
        )
        with st.expander(section_header, expanded=False):
            master_key = f"{selected_course_id}-{sec_title}-master"
            col1, col2 = st.columns([8, 2])
            with col1:
                master_status = st.selectbox(
                    "🎛️ Master Status", options=["---"] + status_options, key=master_key
                )
            with col2:
                if st.button("✅ Apply", key=f"{master_key}-apply"):
                    for idx, item in enumerate(section.get("items", [])):
                        key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{str(item.get('object_index', idx))}"
                        if master_status != "---":
                            statuses[key] = master_status
            st.markdown("---")
            for idx, item in enumerate(section.get("items", [])):
                key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{str(item.get('object_index', idx))}"
                current_status = statuses.get(key, "❌ Not Done")
                badge_color = status_colors.get(current_status, "#000")
                lecture_badge = f"<span style='font-size:0.7em; color:white; background-color:{badge_color}; padding:1px 3px; border-radius:3px;'>{current_status}</span>"
                col_a, col_b, col_c = st.columns([6, 3, 3])
                with col_a:
                    st.markdown(
                        f"{lecture_badge}<br><strong>{item.get('title', 'Untitled Item')}</strong>",
                        unsafe_allow_html=True,
                    )
                with col_b:
                    st.markdown(
                        f"⏱ {item.get('content_summary', 'Unknown')}",
                        unsafe_allow_html=True,
                    )
                with col_c:
                    unique_key = f"{selected_course_id}-{sec_title}-{item.get('title', 'Untitled')}-{str(item.get('object_index', idx))}-status"
                    new_status = st.selectbox(
                        "Status",
                        status_options,
                        index=(
                            status_options.index(current_status)
                            if current_status in status_options
                            else 0
                        ),
                        key=unique_key,
                    )
                    statuses[key] = new_status
                st.markdown("---")


# --- Analytics Dashboard ---
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
        f"✅ **Done:** {done}  ⏳ **In Progress:** {in_progress}  ❌ **Not Done:** {not_done}"
    )
    progress_percent = (done / (done + not_done) * 100) if total > 0 else 0
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


# --- Main Function ---
def main():
    """Main function to run the MyUdemyProgress app."""
    initialize_session_state()
    autosave_setting, preload_enabled, filter_option = render_sidebar()

    if os.path.exists(AUTOSAVE_FILENAME):
        try:
            load_autosave()
            st.sidebar.success("Loaded autosave.json")
        except Exception as e:
            st.sidebar.error(f"Error loading autosave.json: {e}")
    elif (
        preload_enabled
        and st.session_state["json_data"] is None
        and os.path.exists(PRELOAD_FILENAME)
    ):
        try:
            st.session_state["json_data"] = load_json(PRELOAD_FILENAME)
            st.sidebar.success(f"Preloaded {PRELOAD_FILENAME}")
        except Exception as e:
            st.sidebar.error(f"Error preloading {PRELOAD_FILENAME}: {e}")

    handle_file_upload()

    if st.session_state["json_data"] is not None:
        for cid, course in st.session_state["json_data"].items():
            if "statuses" in course:
                for key, value in course["statuses"].items():
                    st.session_state["statuses"][key] = get_ui_status(value)
        json_data = st.session_state["json_data"]
        statuses = st.session_state["statuses"]
        selected_course_id = render_course_selection(json_data)
        render_course_details(
            selected_course_id,
            json_data,
            statuses,
            universal_status_options,
            filter_option,
        )
        show_progress_dashboard(selected_course_id, statuses)
        if autosave_setting:
            try:
                save_autosave()
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
    else:
        st.info("Please upload a JSON file or ensure autosave.json/input.json exists.")


# --- Custom CSS: Increase Scrollbar Width ---
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
