import os

POEMS_DIR = "poems"
TEMPLATE_PATH = "templates/base.html"
OUTPUT_DIR = "site"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

poems = []

# Read poems
for filename in os.listdir(POEMS_DIR):
    if filename.endswith(".txt"):
        path = os.path.join(POEMS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            title = lines[0].replace("Title: ", "")
            content = "\n".join(lines[2:])  # Skip Title, Author, Tags
            slug = os.path.splitext(filename)[0]
            poems.append({"title": title, "content": content, "slug": slug})

# Generate individual poem pages
for p in poems:
    html_content = f"<h2>{p['title']}</h2><pre>{p['content']}</pre>"
    html_content += f"<p><a href='index.html'>← Back to summary</a></p>"
    html = template.replace("{title}", p["title"]).replace("{content}", html_content)
    with open(os.path.join(OUTPUT_DIR, f"{p['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# Generate main page (summary)
main_content = "<ul>"
for p in poems:
    main_content += f"<li><a href='{p['slug']}.html'>{p['title']}</a></li>"
main_content += "</ul>"

main_html = template.replace("{title}", "My Poems").replace("{content}", main_content)
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(main_html)

print(f"Generated {len(poems)} poems in '{OUTPUT_DIR}'")
