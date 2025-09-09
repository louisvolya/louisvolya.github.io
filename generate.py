import os

POEMS_DIR = "poems"  # can contain subdirectories
TEMPLATE_FILE = "templates/index_skeleton.html"
OUTPUT_FILE = "site/index.html"

os.makedirs("site", exist_ok=True)

# Read skeleton template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

poems_html = ""

# Iterate over subdirectories
for root, dirs, files in os.walk(POEMS_DIR):
    # Only consider directories directly under POEMS_DIR
    if root == POEMS_DIR:
        for subdir in dirs:
            folder_path = os.path.join(POEMS_DIR, subdir)
            poems_html += f"<h2>{subdir}</h2>\n"  # folder as summary heading
            poems_html += "<div class='folder'>\n"
            for filename in os.listdir(folder_path):
                if filename.endswith(".txt"):
                    path = os.path.join(folder_path, filename)
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.read().splitlines()
                        if not lines:
                            continue
                        title = lines[0].replace("Title: ", "").strip()
                        content = "\n".join(lines[2:]).strip()  # skip title + blank line
                        poems_html += f"<div class='poem'>\n"
                        poems_html += f"  <div class='poem-title'>{title}</div>\n"
                        poems_html += f"  <div class='poem-content'>{content}</div>\n"
                        poems_html += "</div>\n"
            poems_html += "</div>\n\n"

# Generate index.html
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(template.replace("{poems_html}", poems_html))

print(f"Generated {OUTPUT_FILE} with poems organized by folder.")
