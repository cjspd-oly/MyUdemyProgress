# Changelog

All notable changes to this project will be documented in this file.

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
