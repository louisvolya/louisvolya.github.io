import os

POEMS_DIR = "poems"           # contains subdirectories of poems
TEMPLATE_FILE = "templates/index_skeleton.html"
OUTPUT_DIR = "site"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read skeleton template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

# --- 1) Generate main index.html ---
main_content = "<ul>\n"

for subdir in sorted(os.listdir(POEMS_DIR)):
    folder_path = os.path.join(POEMS_DIR, subdir)
    if not os.path.isdir(folder_path):
        continue
    display_name = subdir.replace("_", " ")
    folder_page = f"{subdir}.html"
    main_content += f"<li><a href='{folder_page}'>{display_name}</a></li>\n"

main_content += "</ul>\n"

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(template.replace("{poems_html}", main_content))

print("Generated main index.html with folder links.")

# --- 2) Generate a page for each folder ---
for subdir in sorted(os.listdir(POEMS_DIR)):
    folder_path = os.path.join(POEMS_DIR, subdir)
    if not os.path.isdir(folder_path):
        continue
    display_name = subdir.replace("_", " ")
    poems_html = f"<h1>{display_name}</h1>\n"

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt"):
            path = os.path.join(folder_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if not lines:
                    continue
                title = lines[0].replace("Title: ", "").strip()
                content = "\n".join(lines[2:]).strip()
                poems_html += f"<div class='poem'>\n"
                poems_html += f"  <div class='poem-title'>{title}</div>\n"
                poems_html += f"  <div class='poem-content'>{content}</div>\n"
                poems_html += "</div>\n"

    # Link back to main page
    poems_html += "<p><a href='index.html'>← Back to main page</a></p>"

    # Generate HTML file for this folder
    output_file = os.path.join(OUTPUT_DIR, f"{subdir}.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template.replace("{poems_html}", poems_html))

    print(f"Generated page for folder '{subdir}'")
