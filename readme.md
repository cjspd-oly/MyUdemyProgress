# 📚 My Udemy Progress

**My Udemy Progress** is a Streamlit-based web application that helps you track your Udemy course progress, manage lesson statuses, and export Markdown reports. The app provides an intuitive UI with autosave, file import, and export functionalities.  
*Note: A detailed changelog will be provided in a separate `changelog.md` file in the future.*

![App Screenshot](#) _(Add screenshot of the UI here)_

---

## 🚀 Features

- **Course-wise and Section-wise Tracking**  
  Easily monitor progress across entire courses and within individual sections.
- **Customizable Status Options**  
  Choose from: ❌ Not Done, ⏳ In Progress, ✅ Done, ⭐ Important, ⏭ Skip, 🚫 Ignore.
- **Import JSON Data**  
  Load your Udemy data via JSON (preload support available with `input.json`).
- **Autosave Progress**  
  Automatically save your progress for easy recovery.
- **Export Markdown Reports**  
  - Individual Markdown file per course  
  - Combined Markdown file for all courses  
  - ZIP download of all Markdown files
- **User-friendly Interface**  
  Update statuses with intuitive dropdowns and master status controls.
- **Instant Top-Positioned Progress Dashboard**  
  View updated progress analytics instantly at the top of the app.
- **Enhanced Code Modularity**  
  A scalable and well-documented codebase for easier maintenance and future feature additions.

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
source venv/bin/activate  # On Windows, use venv\Scripts\activate
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

- **Upload your Udemy JSON file** (downloaded via API or manually exported).  
- Or, enable **Preload JSON** to automatically load `input.json`.

### 2️⃣ Track Your Progress

- Update lesson statuses using the **dropdown** next to each lesson.
- Use the **Master Status** control in each section to update all lessons at once.
- The progress dashboard at the top updates instantly with every change.

### 3️⃣ Save Your Progress

- Enable **Autosave** to save changes automatically.
- Click **"Save All Changes"** (or use the sidebar Save All button) to manually save progress.  
  *Note: When saving, statuses are stored in plain text (without emojis) in the JSON file.*

### 4️⃣ Export Reports

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
└── 📄 README.md           # Documentation
```

---

## 📂 Legacy Development (`dev/` Folder)

The `dev/` folder contains legacy or experimental code used during initial development. It is retained for reference but is not required for the main application.

🚨 **Note:** Features in this folder may be outdated or unsupported in the current version.

---

## 📂 Demo (`demo/` Folder)

The `demo/` folder contains sample files and example data to showcase the app’s functionality. Use these files to explore features before importing your own Udemy data.

---

## 🎨 Customization

### 🔹 Change Status Options

Modify the `status_options` list in `app.py`:

```python
status_options = ["❌ Not Done", "⏳ In Progress", "✅ Done", "⭐ Important", "⏭ Skip", "🚫 Ignore"]
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