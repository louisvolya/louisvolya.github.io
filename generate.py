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


# --- 1) Generate homepage (books) ---
homepage_content = "<h1>Books</h1>\n<ul>\n"

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
    poem_links = []
    for i, filename in enumerate(sorted(poems)):
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

        # Prev/Next links
        nav_parts = []
        if i > 0:
            prev_title_line = open(os.path.join(book_path, sorted(poems)[i-1]), encoding="utf-8").read().splitlines()[0]
            prev_title = prev_title_line.replace("Title: ", "").strip()
            prev_file = f"{os.path.splitext(sorted(poems)[i-1])[0]}.html"
            nav_parts.append(f"<a href='{prev_file}'>&larr; {prev_title}</a>")
        if i < len(poems) - 1:
            next_title_line = open(os.path.join(book_path, sorted(poems)[i+1]), encoding="utf-8").read().splitlines()[0]
            next_title = next_title_line.replace("Title: ", "").strip()
            next_file = f"{os.path.splitext(sorted(poems)[i+1])[0]}.html"
            nav_parts.append(f"<a href='{next_file}'>{next_title} &rarr;</a>")
        nav_html = ""
        if nav_parts:
            nav_html = "<div class='nav-buttons'>" + "".join(nav_parts) + "</div>"

        poem_html = (
            f"<h2>{title}</h2>\n"
            f"<div class='poem-box'>{content}</div>\n"
            f"{nav_html}\n"
            f"<p><a href='../index.html'>← Menu principal</a></p>"
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
        chapter_poems = [f for f in sorted(os.listdir(chapter_path)) if f.endswith(".txt")]

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

            # Prev/Next links
            nav_parts = []
            if i > 0:
                prev_title_line = open(os.path.join(chapter_path, chapter_poems[i-1]), encoding="utf-8").read().splitlines()[0]
                prev_title = prev_title_line.replace("Title: ", "").strip()
                prev_file = f"{os.path.splitext(chapter_poems[i-1])[0]}.html"
                nav_parts.append(f"<a href='{prev_file}'>&larr; {prev_title}</a>")
            if i < len(chapter_poems) - 1:
                next_title_line = open(os.path.join(chapter_path, chapter_poems[i+1]), encoding="utf-8").read().splitlines()[0]
                next_title = next_title_line.replace("Title: ", "").strip()
                next_file = f"{os.path.splitext(chapter_poems[i+1])[0]}.html"
                nav_parts.append(f"<a href='{next_file}'>{next_title} &rarr;</a>")
            nav_html = ""
            if nav_parts:
                nav_html = "<div class='nav-buttons'>" + "".join(nav_parts) + "</div>"

            poem_html = (
                f"<h2>{title}</h2>\n"
                f"<div class='poem-box'>{content}</div>\n"
                f"{nav_html}\n"
                f"<p><a href='../../index.html'>← Menu principal</a></p>"
            )

            with open(poem_file_path, "w", encoding="utf-8") as f:
                f.write(wrap(poem_html))

            chapter_poem_links.append((title, poem_file_name))

        # Chapter main page
        chapter_page_html = f"<h1>{chapter_display_name}</h1>\n<ul>\n"
        for title, link in chapter_poem_links:
            chapter_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
        chapter_page_html += f"</ul>\n<p><a href='../index.html'>← Menu principal</a></p>"

        with open(os.path.join(chapter_output_dir, f"{chapter}.html"), "w", encoding="utf-8") as f:
            f.write(wrap(chapter_page_html))

        chapter_links.append((chapter_display_name, f"{chapter}/{chapter}.html"))

    # --- Generate book main page ---
    book_page_html = f"<h1>{book_display_name}</h1>\n<ul>\n"
    for title, link in poem_links:
        book_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
    for chapter_name, link in chapter_links:
        book_page_html += f"<li><a href='{link}'>{chapter_name}</a></li>\n"
    book_page_html += "</ul>\n<p><a href='../index.html'>← Menu principal</a></p>"

    with open(os.path.join(book_output_dir, f"{book}.html"), "w", encoding="utf-8") as f:
        f.write(wrap(book_page_html))

    print(f"Generated book '{book}' with chapters and poems.")
