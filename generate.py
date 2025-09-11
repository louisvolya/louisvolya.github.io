import os

POEMS_DIR = "poems"       # input poems directory
OUTPUT_DIR = "site"       # output site directory
TEMPLATE_FILE = "templates/index_skeleton.html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML template
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
    return -1  # files without number go first


# --- 1) Generate homepage (books) ---
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


# --- 2) Generate book pages, chapter pages, and poem pages ---
for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue

    book_display_name = book.replace("_", " ")
    book_output_dir = os.path.join(OUTPUT_DIR, book)
    os.makedirs(book_output_dir, exist_ok=True)

    chapters = []
    poems = []

    # Classify contents: chapters or poems
    for item in sorted(os.listdir(book_path)):
        item_path = os.path.join(book_path, item)
        if os.path.isdir(item_path):
            chapters.append(item)
        elif item.endswith(".txt"):
            poems.append(item)

    # --- Generate poem pages (direct poems in book, no chapters) ---
    poems = sorted(poems, key=poem_sort_key)
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

        # Prev/Next buttons
        nav_html = build_nav(poems, i, book_path)

        # Link back to the book page
        poem_html = (
            f"<h2>{title}</h2>\n"
            f"<div class='poem-box'>{content}</div>\n"
            f"{nav_html}\n"
            f"<p><a href='{book}.html'>← {book_display_name}</a></p>"
        )

        with open(poem_file_path, "w", encoding="utf-8") as f:
            f.write(wrap(poem_html))

        poem_links.append((title, poem_file_name))

    # --- Generate chapter pages ---
    chapter_links = []
    for chapter in sorted(chapters):
        chapter_path = os.path.join(book_path, chapter)
        chapter_output_dir = os.path.join(book_output_dir, chapter)
        os.makedirs(chapter_output_dir, exist_ok=True)

        chapter_display_name = chapter.replace("_", " ")
        chapter_poems = [f for f in os.listdir(chapter_path) if f.endswith(".txt")]
        chapter_poems = sorted(chapter_poems, key=poem_sort_key)

        chapter_poem_links = []
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

            # Prev/Next buttons
            nav_html = build_nav(chapter_poems, i, chapter_path)

            # Link back to chapter page
            poem_html = (
                f"<h2>{title}</h2>\n"
                f"<div class='poem-box'>{content}</div>\n"
                f"{nav_html}\n"
                f"<p><a href='{chapter}.html'>← {chapter_display_name}</a></p>"
            )

            with open(poem_file_path, "w", encoding="utf-8") as f:
                f.write(wrap(poem_html))

            chapter_poem_links.append((title, poem_file_name))

        # Chapter main page → link back to root menu
        chapter_page_html = f"<h1>{chapter_display_name}</h1>\n<ul>\n"
        for title, link in chapter_poem_links:
            chapter_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
        chapter_page_html += f"</ul>\n<p><a href='../../../index.html'>← Menu principal</a></p>"

        with open(os.path.join(chapter_output_dir, f"{chapter}.html"), "w", encoding="utf-8") as f:
            f.write(wrap(chapter_page_html))

        chapter_links.append((chapter_display_name, f"{chapter}/{chapter}.html"))

    # --- Generate book main page ---
    book_page_html = f"<h1>{book_display_name}</h1>\n<ul>\n"
    for title, link in poem_links:
        book_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
    for chapter_name, link in chapter_links:
        book_page_html += f"<li><a href='{link}'>{chapter_name}</a></li>\n"
    # book main page → link back to root menu
    book_page_html += "</ul>\n<p><a href='../../index.html'>← Menu principal</a></p>"

    with open(os.path.join(book_output_dir, f"{book}.html"), "w", encoding="utf-8") as f:
        f.write(wrap(book_page_html))

    print(f"Generated book '{book}' with chapters and poems.")
    
    #tototata
