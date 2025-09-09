import os

POEMS_DIR = "poems"
TEMPLATE_PATH = "templates/base.html"
OUTPUT_DIR = "site"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load template
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

poems = []

# Read poems from .txt files
for filename in os.listdir(POEMS_DIR):
    if filename.endswith(".txt"):
        path = os.path.join(POEMS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            title = lines[0].replace("Title: ", "")
            author = lines[1].replace("Author: ", "")
            content = "\n".join(lines[3:])
            slug = os.path.splitext(filename)[0]  # filename without extension
            poems.append({
                "title": title,
                "author": author,
                "content": content,
                "slug": slug
            })

# Generate poem pages
for p in poems:
    html_content = f"<h2>{p['title']}</h2><p><em>{p['author']}</em></p><pre>{p['content']}</pre>"
    html_content += f"<p><a href='index.html'>← Back to summary</a></p>"
    html = template.replace("{title}", p["title"]).replace("{content}", html_content)
    with open(os.path.join(OUTPUT_DIR, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# Generate main page
main_content = "<ul>"
for p in poems:
    main_content += f"<li><a href='{p['slug']}.html'>{p['title']} ({p['author']})</a></li>"
main_content += "</ul>"

main_html = template.replace("{title}", "My Poems").replace("{content}", main_content)
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(main_html)

print(f"Generated {len(poems)} poems in '{OUTPUT_DIR}'")
