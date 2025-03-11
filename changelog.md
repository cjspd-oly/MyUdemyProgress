# Changelog

All notable changes to this project will be documented in this file.

---

## v1.2.0 - [2025-03-11]

### Added
- **Autosave Preload:**  
  The app now preloads `autosave.json`, ensuring that both course data and statuses persist across sessions. This allows users to continue from where they left off.
- **Expand All Toggle:**  
  Introduced a sidebar toggle for expanding or collapsing all sections when the lecture filter is set to "All." For other filter options, sections expand only if they contain one or more matching lectures.
- **Universal Status List:**  
  A centralized status list ensures consistency across the app for filtering and updating statuses.
- **Section Completion Progress:**  
  Each section header now displays its completion rate in the format `X/Y` (e.g., `4/10` lectures completed).
- **Scrollbar Enhancement:**  
  Adjusted the scrollbar width using custom CSS to improve usability.

### Fixed
- **Status Loading from Autosave:**  
  Resolved an issue where statuses were not correctly loaded from `autosave.json`, causing all lectures to default to "Not Done."
- **Section Expansion Behavior:**  
  Fixed an issue where sections did not properly collapse or expand based on the selected filter and toggle settings.

### Improved
- **Code Organization:**  
  Autosave functionality is now separate from settings, keeping `autosave.json` focused on progress tracking while `settings.json` stores user preferences.
- **Status Conversion Handling:**  
  The app now automatically converts older plain-text status values (e.g., `"Done"`) to their emoji-enhanced counterparts (e.g., `"✅ Done"`).
- **User Interface Adjustments:**  
  - The status badge now appears as a smaller element above lecture titles for better readability.
  - Enhanced layout and responsiveness for better user experience.

---

## v1.1.2 - [2025-02-25]

### Fixed
- **File Path Fix for Streamlit Hosting:**  
  Updated the file path constants to use relative paths instead of dynamically joining with the script directory. This ensures that the app correctly locates `data/autosave.json` and `data/input.json` when hosted on Streamlit Cloud.

---

## v1.1.1 - [2025-02-24]

### Added
- **UI Enhancement:**
  Added a placeholder "---" to the Master Status dropdown to prevent accidental bulk updates when no meaningful status is selected.

---

## v1.1.0 - [2025-02-22]

### Added
- **Instant Top-Positioned Progress Dashboard:**  
  The dashboard now appears at the top of the app and updates instantly on any status change (both master and individual updates).
- **Plain-Text Status Saving:**  
  Statuses are displayed with emoji enhancements in the UI but are saved in plain text in the JSON file for better compatibility.
- **Improved Code Modularity and Documentation:**  
  The codebase has been refactored into modular helper functions with detailed inline comments and docstrings, making the app more scalable and maintainable.
- **Enhanced UI/UX:**  
  Updated status options and UI elements (dropdowns, master status controls) to provide a more intuitive and responsive user experience.

### Changed
- **Widget Rendering Optimization:**  
  Reduced redundant re-renders for better performance, particularly with large datasets.
- **README.md Updates:**  
  The documentation now reflects the new features and improvements introduced in this version.

---

## v1.0.0 - [2025-02-05]

### Initial Release
- **Course and Section Tracking:**  
  Track progress on a per-course and per-section basis.
- **Customizable Status Options:**  
  Statuses include: Not Done, In Progress, Done, Important, Skip, and Ignore.
- **JSON Data Import:**  
  Support for importing Udemy course data via JSON.
- **Autosave Functionality:**  
  Automatically saves progress for easy recovery.
- **Markdown Export:**  
  Generate and download Markdown reports individually (per course) or combined, including ZIP download of all Markdown files.
- **User-Friendly Interface:**  
  Utilizes dropdown-based status updates with basic emoji enhancements and formatting.
- **Preload JSON Feature:**  
  Option to preload a JSON file (`input.json`) for quick startup.
