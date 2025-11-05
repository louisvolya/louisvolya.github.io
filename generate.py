import os

POEMS_DIR = "poems"       # input poems directory
OUTPUT_DIR = "site"       # output site directory
TEMPLATE_FILE = "templates/index_skeleton.html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()


def wrap(content: str) -> str:
    """Insert content into template."""
    return template.replace("{poems_html}", content)


def build_nav(files, idx, base_path):
    """Build navigation bar with prev on left, next on right."""
    prev_html = "<span></span>"
    next_html = "<span></span>"

    if idx > 0:
        prev_title_line = open(os.path.join(base_path, files[idx-1]), encoding="utf-8").read().splitlines()[0]
        prev_title = prev_title_line.replace("Title: ", "").strip()
        prev_file = f"{os.path.splitext(files[idx-1])[0]}.html"
        prev_html = f"<a href='{prev_file}'>&larr; {prev_title}</a>"

    if idx < len(files) - 1:
        next_title_line = open(os.path.join(base_path, files[idx+1]), encoding="utf-8").read().splitlines()[0]
        next_title = next_title_line.replace("Title: ", "").strip()
        next_file = f"{os.path.splitext(files[idx+1])[0]}.html"
        next_html = f"<a href='{next_file}'>{next_title} &rarr;</a>"

    return f"<div class='nav-buttons' style='display:flex;justify-content:space-between;width:100%;max-width:600px;margin-top:1rem;'>{prev_html}{next_html}</div>"


def poem_sort_key(filename: str) -> int:
    """Extract leading number before '_' in filename for numeric sorting. Treat 0 as first."""
    base = os.path.splitext(filename)[0]
    if "_" in base:
        prefix = base.split("_", 1)[0]
        if prefix.isdigit():
            return int(prefix)
    return -1  


# Generate homepage
homepage_content = "<h1>Œuvres</h1>\n<ul>\n"

for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue
    display_name = book.replace("_", " ")
    book_index = f"site/{book}/{book}.html"
    homepage_content += f"<li><a href='{book_index}'>{display_name}</a></li>\n"

homepage_content += "</ul>\n"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(wrap(homepage_content))

print("Generated homepage with book links.")


# Generate books and poems
for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue

    book_display_name = book.replace("_", " ")
    book_output_dir = os.path.join(OUTPUT_DIR, book)
    os.makedirs(book_output_dir, exist_ok=True)

    # Separate items into poems and chapters
    chapters = []
    poems = []

    for item in sorted(os.listdir(book_path)):
        item_path = os.path.join(book_path, item)
        if os.path.isdir(item_path):
            chapters.append(item)
        elif item.endswith(".txt"):
            poems.append(item)

    poems = sorted(poems, key=poem_sort_key)

    # --- Generate individual poem pages directly under the book ---
    poem_links = []
    for i, filename in enumerate(poems):
        poem_path = os.path.join(book_path, filename)
        with open(poem_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()

        lines = raw_content.splitlines()
        if not lines:
            continue

        title = lines[0].replace("Title: ", "").strip()
        content = "\n".join(lines[2:]).strip()

        poem_file_name = f"{os.path.splitext(filename)[0]}.html"
        poem_file_path = os.path.join(book_output_dir, poem_file_name)

        nav_html = build_nav(poems, i, book_path)

        poem_html = (
            f"<h2>{title}</h2>\n"
            f"<div class='poem-box'>{content}</div>\n"
            f"{nav_html}\n"
            f"<p><a href='{book}.html'>← {book_display_name}</a></p>"
        )

        with open(poem_file_path, "w", encoding="utf-8") as f:
            f.write(wrap(poem_html))

        poem_links.append((title, poem_file_name))

    # --- Process chapter directories but DO NOT generate pages for them ---
    chapter_sections = []
    for chapter in sorted(chapters):
        chapter_path = os.path.join(book_path, chapter)
        chapter_output_dir = os.path.join(book_output_dir, chapter)
        os.makedirs(chapter_output_dir, exist_ok=True)

        chapter_display_name = chapter.replace("_", " ")
        chapter_poems = [f for f in os.listdir(chapter_path) if f.endswith(".txt")]
        chapter_poems = sorted(chapter_poems, key=poem_sort_key)

        chapter_section = f"<h2>{chapter_display_name}</h2>\n<ul>\n"

        for i, filename in enumerate(chapter_poems):
            poem_path = os.path.join(chapter_path, filename)
            with open(poem_path, "r", encoding="utf-8") as f:
                raw_content = f.read().strip()

            lines = raw_content.splitlines()
            if not lines:
                continue

            title = lines[0].replace("Title: ", "").strip()
            content = "\n".join(lines[2:]).strip()

            poem_file_name = f"{os.path.splitext(filename)[0]}.html"
            poem_file_path = os.path.join(chapter_output_dir, poem_file_name)

            nav_html = build_nav(chapter_poems, i, chapter_path)

            poem_html = (
                f"<h2>{title}</h2>\n"
                f"<div class='poem-box'>{content}</div>\n"
                f"{nav_html}\n"
                f"<p><a href='../{book}.html'>← {book_display_name}</a></p>"
            )

            with open(poem_file_path, "w", encoding="utf-8") as f:
                f.write(wrap(poem_html))

            chapter_section += f"<li><a href='{chapter}/{poem_file_name}'>{title}</a></li>\n"

        chapter_section += "</ul>\n"
        chapter_sections.append(chapter_section)

    # --- Build the single book page ---
    book_page_html = f"<h1>{book_display_name}</h1>\n"

    if poem_links:
        book_page_html += "<ul>\n"
        for title, link in poem_links:
            book_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
        book_page_html += "</ul>\n"

    book_page_html += "\n".join(chapter_sections)
    book_page_html += "<p><a href='../../index.html'>← Menu principal</a></p>"

    with open(os.path.join(book_output_dir, f"{book}.html"), "w", encoding="utf-8") as f:
        f.write(wrap(book_page_html))

    print(f"Generated book '{book}' with hierarchical poem list.")
