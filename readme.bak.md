# 📚 My Udemy Progress

**My Udemy Progress** is a Streamlit-based web application that helps you track your Udemy course progress, manage lesson statuses, and export Markdown reports. The app provides an intuitive UI with autosave, file import, and export functionalities.  
*Note: A detailed changelog will be provided in a separate `changelog.md` file in the future.*

![App Screenshot](#)  
*(Add screenshot of the UI here)*

---

## 🚀 Features

- **Course-wise and Section-wise Tracking**  
  Monitor your overall progress and drill down into individual sections for detailed insights.
- **Customizable Status Options**  
  Easily update lesson statuses using a universal status list: ❌ Not Done, ⏳ In Progress, ✅ Done, ⭐ Important, ⏭ Skip, 🚫 Ignore.
- **Import & Autosave Data**  
  Import your Udemy JSON data (with preload support via `input.json`) and autosave your progress in a separate `autosave.json` file.
- **Export Markdown Reports**  
  Download:
  - An individual Markdown file per course  
  - A combined Markdown file for all courses  
  - A ZIP archive containing all Markdown files
- **Instant Progress Dashboard**  
  A top-positioned dashboard provides updated progress analytics as you update statuses.
- **Expand/Collapse Sections**  
  Use the sidebar toggle to expand or collapse all sections (when the filter is set to "All"). For other filters, sections expand automatically if they contain one or more matching lectures.
- **Enhanced User Interface**  
  - Lesson status badges are displayed on a new, smaller line above the lesson title.
  - Improved scrollbar width for a better browsing experience.
- **Robust and Modular Codebase**  
  Designed for easy maintenance and future feature additions, with improved file path handling for Streamlit hosting environments.

---

## 📦 Installation

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/cjspd.oly/my-udemy-progress.git
cd my-udemy-progress
```

### 2️⃣ Set Up a Virtual Environment (Recommended)

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

### 4️⃣ Run the App

```sh
streamlit run app.py
```

---

## 🛠️ Usage

### 1️⃣ Load Your Udemy Data

- **Upload your Udemy JSON file** (downloaded via API or manually exported), or
- Enable **Preload JSON** to automatically load `input.json`.

### 2️⃣ Track Your Progress

- Update lesson statuses using the **dropdown** next to each lesson.
- Use the **Master Status** control to update all lessons in a section at once.
- The progress dashboard at the top updates instantly with every change.

### 3️⃣ Expand/Collapse Sections

- Use the **Expand All Sections** toggle in the sidebar to force all sections to be expanded when the filter is set to "All."
- For any other filter, sections expand automatically only if they contain one or more lectures matching the filter.

### 4️⃣ Save Your Progress

- Enable **Autosave** in the sidebar (this setting is saved in the settings file) to save changes automatically.
- Alternatively, click **"Save All Changes"** (or the sidebar Save All button) to manually save progress.  
  *Note: When saving, lesson statuses are stored in plain text (without emojis) in the autosave file (`autosave.json`).*

### 5️⃣ Export Reports

- **Download individual Markdown files** per course.
- **Download a combined Markdown file** for all courses.
- **Download a ZIP file** containing all Markdown files.

---

## 📂 File Structure

```
📂 my-udemy-progress/
├── 📄 app.py              # Main Streamlit app script
├── 📜 requirements.txt    # Python dependencies
├── 📂 data/
│   ├── input.json         # Optional preload JSON file
│   ├── autosave.json      # Autosaved progress file (plain statuses)
├── 📂 dev/                # Legacy development folder (for reference)
├── 📂 demo/               # Demo folder with example files & sample data
├── 📂 personal/           # Personal Stuff (Ignore this)
└── 📄 README.md           # Project documentation (this file)
```

---

## 📂 Legacy Development (`dev/` Folder)

The `dev/` folder contains legacy or experimental code used during initial development. This folder is maintained for reference only; features here may be outdated or unsupported in the current version.

---

## 📂 Demo (`demo/` Folder)

The `demo/` folder includes sample files and example data to showcase the app’s functionality. Explore these files before importing your own Udemy data.

---

## 🎨 Customization

### 🔹 Change Status Options

Modify the `universal_status_options` list in `app.py`:

```python
universal_status_options = ["❌ Not Done", "⏳ In Progress", "✅ Done", "⭐ Important", "⏭ Skip", "🚫 Ignore"]
```

### 🔹 Preload Default JSON File

Set the preload file path in `app.py`:

```python
PRELOAD_FILENAME = "data/input.json"
```

### 🔹 Modify Export File Names

Edit the `sanitize_filename()` function in `app.py` to customize exported file names.

---

## 🤝 Contributing

Contributions are welcome! 🚀  
Feel free to:
- **Report bugs**
- **Suggest new features**
- **Improve UI/UX**
- **Submit pull requests**

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 📧 Contact

For queries or suggestions, please reach out!

---