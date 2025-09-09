import os

POEMS_DIR = "poems"
TEMPLATE_FILE = "templates/index_skeleton.html"
OUTPUT_FILE = "site/index.html"

os.makedirs("site", exist_ok=True)

# Read skeleton template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

poems_html = ""

# Read all poems
for filename in os.listdir(POEMS_DIR):
    if filename.endswith(".txt"):
        path = os.path.join(POEMS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if not lines:
                continue
            title = lines[0].replace("Title: ", "").strip()
            content = "\n".join(lines[2:]).strip()  # skip title + blank line
            poems_html += f"<div class='poem'>\n"
            poems_html += f"  <div class='poem-title'>{title}</div>\n"
            poems_html += f"  <div class='poem-content'>{content}</div>\n"
            poems_html += "</div>\n\n"

# Generate index.html
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(template.replace("{poems_html}", poems_html))

print(f"Generated {OUTPUT_FILE} with {len(os.listdir(POEMS_DIR))} poems.")
