import json

def generate_markdown_todo(json_data):
    STATUS_OPTIONS = {
        "checkbox": "☑️ Check",
        "important": "❗ Important",
        "skip": "⏭️ Skip",
        "ignore": "🚫 Ignore",
        "done": "✅ Done",
        "not_done": "⬜ Not Done"
    }
    
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
            
            markdown += f"### {section_title} ({content_length}, {lecture_count} lectures)\n\n"
            
            markdown += "| 🆗 Status | 📚 Title | ⏳ Duration | 🔗 Link |\n"
            markdown += "|----|------------------|-----------|-----------|\n"
            
            for item in section.get("items", []):
                item_title = item.get("title", "Untitled Item")
                content_summary = item.get("content_summary", "Unknown Duration")
                learn_url = item.get("learn_url", "#")
                status = STATUS_OPTIONS.get("not_done", "⬜ Not Done")  # Default status
                
                markdown += f"| {status} | **{item_title}** | {content_summary} | [▶ Learn]({learn_url}) |\n"
            
            markdown += "\n"
        
        markdown += "---\n\n"
    
    return markdown

# Read JSON input from file
with open("input.json", "r", encoding="utf-8") as file:
    parsed_json = json.load(file)

# Generate markdown content
markdown_todo = generate_markdown_todo(parsed_json)

# Save output to a Markdown file
with open("output.md", "w", encoding="utf-8") as md_file:
    md_file.write(markdown_todo)

print("Markdown file 'output.md' generated successfully.")
