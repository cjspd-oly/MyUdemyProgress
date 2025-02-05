# 📚 My Udemy Progress

**My Udemy Progress** is a Streamlit-based web application that helps you track your Udemy course progress, manage lesson statuses, and export markdown reports. The app provides an intuitive UI with autosave, file import, and export functionalities.

![App Screenshot](#) *(Add screenshot of the UI here)*

---

## 🚀 Features

- 📂 **Course-wise and Section-wise tracking**
- 🏷️ **Customizable status options** (Not Done, In Progress, Done, Important, Skip, Ignore)
- 📥 **Import JSON data** from Udemy
- 💾 **Autosave progress** for easy recovery
- 📤 **Export Markdown reports**
  - Individually (per course)
  - Combined (all courses)
  - Zip download (all Markdown files)
- 🖥️ **User-friendly interface** with dropdown-based status updates
- 🔄 **Preload JSON file (`input.json`)**
- 🖱️ **Easy navigation** between courses
- 🎨 **Enhanced UI with emojis & formatting**

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/my-udemy-progress.git
cd my-udemy-progress
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App
```bash
streamlit run app.py
```

---

## 🛠️ Usage

### 1️⃣ Load Your Udemy Data
- Upload your **Udemy JSON file** (downloaded via API or manually exported).
- Or, enable **Preload JSON** to automatically load `input.json`.

### 2️⃣ Track Your Progress
- Use the **dropdown** next to each lesson to set your progress status.
- Status options: ✅ Done, 🚀 In Progress, 🔴 Not Done, ⭐ Important, ❌ Skip, 🚫 Ignore.

### 3️⃣ Save Your Progress
- Enable **Autosave** to save changes automatically.
- Click **"Save All Changes"** to manually save.

### 4️⃣ Export Reports
- **Download Markdown files** per course.
- **Get a combined Markdown file** with all courses.
- **Download a ZIP** containing all markdown files.

---

## File Structure:  


```
📂 my-udemy-progress/
├── 📄 app.py              # Streamlit app script
├── 📜 requirements.txt    # Python dependencies
├── 📂 data/
│   ├── input.json         # Optional preload JSON file
│   ├── autosave.json      # Autosaved progress file
├── 📂 dev/                # Legacy development folder (see note below)
├── 📂 demo/                # demo folder (see note below)
└── 📄 README.md           # Documentation
```

## 📂 Legacy Development (`dev/` Folder)

The `dev/` folder contains legacy or experimental code that was used during the initial development phase. It is retained for reference purposes but is not required for the main application.  

🚨 **Note:** Features in this folder may be outdated, incomplete, or unsupported in the current version of the app.

## 📂 Demo (`demo/` Folder)

The `demo/` folder contains example files and sample data to showcase the app’s features. Use these files to explore the functionality before importing your own Udemy data.


---

## 🎨 Customization

### 🔹 Change Status Options
Modify the `status_options` list in `app.py`:
```python
status_options = ["Not Done", "In Progress", "Done", "Important", "Skip", "Ignore"]
```

### 🔹 Preload Default JSON File
Set `PRELOAD_FILENAME` in `app.py`:
```python
PRELOAD_FILENAME = "input.json"
```

### 🔹 Modify Export File Names
Edit the `sanitize_filename()` function to customize exported file names.

---

## 🤝 Contributing

We welcome contributions! 🚀 Feel free to:
- **Report bugs**
- **Suggest new features**
- **Improve UI/UX**
- **Submit pull requests**

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 📧 Contact

For queries or suggestions, feel free to reach out!

---

Would you like any additional details or customizations in the README? 😊