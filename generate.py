import os
import re

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
        prev_title_line = open(os.path.join(base_path, files[idx - 1]), encoding="utf-8").read().splitlines()[0]
        prev_title = prev_title_line.replace("Title: ", "").strip()
        prev_file = f"{os.path.splitext(files[idx - 1])[0]}.html"
        prev_html = f"<a href='{prev_file}'>&larr; {prev_title}</a>"

    if idx < len(files) - 1:
        next_title_line = open(os.path.join(base_path, files[idx + 1]), encoding="utf-8").read().splitlines()[0]
        next_title = next_title_line.replace("Title: ", "").strip()
        next_file = f"{os.path.splitext(files[idx + 1])[0]}.html"
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


def format_theater_text(text: str) -> str:
    """Apply theater-specific formatting to the poem content."""
    formatted_lines = []
    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            formatted_lines.append("<br>")
            continue

        # ACTE or SCÈNE standalone line
        if re.match(r"^(ACTE|SCÈNE)\s+[IVXLC\d]+\.?$", stripped, re.IGNORECASE):
            formatted_lines.append(f"<div style='text-align:center;font-weight:bold;margin:1em 0;'>{stripped}</div>")
            continue

        # Dialogue line: NAME: text
        if re.match(r"^[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸÆŒ' \-]+:", stripped):
            parts = stripped.split(":", 1)
            name = parts[0].strip()
            speech = parts[1].strip() if len(parts) > 1 else ""
            formatted_lines.append(f"<p><strong>{name}:</strong> {speech}</p>")
            continue

        # Otherwise: didascaly (stage direction)
        formatted_lines.append(f"<div style='text-align:center;font-style:italic;margin:0.5em 0;'>{stripped}</div>")

    return "\n".join(formatted_lines)


# --- Generate homepage ---
homepage_content = "<h1>Œuvres</h1>\n<ul>\n"

# Collect book metadata before writing homepage
books_info = []

for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue

    chapters = [d for d in os.listdir(book_path) if os.path.isdir(os.path.join(book_path, d))]
    poems = [f for f in os.listdir(book_path) if f.endswith(".txt")]

    books_info.append((book, poems, chapters))

# Build homepage links dynamically based on folder content
for book, poems, chapters in books_info:
    display_name = book.replace("_", " ")
    if len(poems) == 1 and not chapters:
        # Single poem only — homepage links directly to that poem
        poem_filename = os.path.splitext(poems[0])[0] + ".html"
        homepage_content += f"<li><a href='site/{book}/{poem_filename}'>{display_name}</a></li>\n"
    else:
        # Regular book with multiple poems or chapters
        homepage_content += f"<li><a href='site/{book}/{book}.html'>{display_name}</a></li>\n"

homepage_content += "</ul>\n"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(wrap(homepage_content))

print("Generated homepage with adaptive book/poem links.")


# --- Generate books and poems ---
for book, poems, chapters in books_info:
    book_path = os.path.join(POEMS_DIR, book)
    book_output_dir = os.path.join(OUTPUT_DIR, book)
    os.makedirs(book_output_dir, exist_ok=True)
    book_display_name = book.replace("_", " ")

    poems = sorted(poems, key=poem_sort_key)

    # Case 1: Folder has only one poem and no chapters → generate only that poem page
    if len(poems) == 1 and not chapters:
        filename = poems[0]
        poem_path = os.path.join(book_path, filename)

        with open(poem_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()

        lines = raw_content.splitlines()
        if not lines:
            continue

        title = lines[0].replace("Title: ", "").strip()
        is_theater = any("Type: Théâtre" in line for line in lines[:3])

        content = "\n".join(lines[2:]).strip()
        if is_theater:
            content = format_theater_text(content)
        else:
            content = f"<div class='poem-box'>{content}</div>"

        poem_file_name = f"{os.path.splitext(filename)[0]}.html"
        poem_file_path = os.path.join(book_output_dir, poem_file_name)

        poem_html = (
            f"<h2>{title}</h2>\n"
            f"{content}\n"
            f"<p><a href='../../index.html'>← Menu principal</a></p>"
        )

        with open(poem_file_path, "w", encoding="utf-8") as f:
            f.write(wrap(poem_html))

        print(f"Generated single-poem page for '{book}'.")
        continue  # Skip book page creation

    # Case 2: Folder has multiple poems or chapters → generate normal book structure
    poem_links = []
    for i, filename in enumerate(poems):
        poem_path = os.path.join(book_path, filename)
        with open(poem_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()

        lines = raw_content.splitlines()
        if not lines:
            continue

        title = lines[0].replace("Title: ", "").strip()
        is_theater = any("Type: Théâtre" in line for line in lines[:3])
        content = "\n".join(lines[2:]).strip()
        if is_theater:
            content = format_theater_text(content)
        else:
            content = f"<div class='poem-box'>{content}</div>"

        poem_file_name = f"{os.path.splitext(filename)[0]}.html"
        poem_file_path = os.path.join(book_output_dir, poem_file_name)

        nav_html = build_nav(poems, i, book_path)

        poem_html = (
            f"<h2>{title}</h2>\n"
            f"{content}\n"
            f"{nav_html}\n"
            f"<p><a href='{book}.html'>← {book_display_name}</a></p>"
        )

        with open(poem_file_path, "w", encoding="utf-8") as f:
            f.write(wrap(poem_html))

        poem_links.append((title, poem_file_name))

    # Process chapter directories
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
            is_theater = any("Type: Théâtre" in line for line in lines[:3])
            content = "\n".join(lines[2:]).strip()
            if is_theater:
                content = format_theater_text(content)
            else:
                content = f"<div class='poem-box'>{content}</div>"

            poem_file_name = f"{os.path.splitext(filename)[0]}.html"
            poem_file_path = os.path.join(chapter_output_dir, poem_file_name)

            nav_html = build_nav(chapter_poems, i, chapter_path)

            poem_html = (
                f"<h2>{title}</h2>\n"
                f"{content}\n"
                f"{nav_html}\n"
                f"<p><a href='../{book}.html'>← {book_display_name}</a></p>"
            )

            with open(poem_file_path, "w", encoding="utf-8") as f:
                f.write(wrap(poem_html))

            chapter_section += f"<li><a href='{chapter}/{poem_file_name}'>{title}</a></li>\n"

        chapter_section += "</ul>\n"
        chapter_sections.append(chapter_section)

    # Build book page
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
