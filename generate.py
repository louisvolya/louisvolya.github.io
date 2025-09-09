import os

POEMS_DIR = "poems"       # Input poems directory
OUTPUT_DIR = "site"       # Output site directory
TEMPLATE_FILE = "templates/index_skeleton.html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the HTML template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

# --- 1) Generate homepage ---
homepage_content = "<ul>\n"

for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue
    display_name = book.replace("_", " ")
    # Link to the book's main page inside its directory
    book_index = f"{book}/{book}.html"
    homepage_content += f"<li><a href='{book_index}'>{display_name}</a></li>\n"

homepage_content += "</ul>\n"

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(template.replace("{poems_html}", homepage_content))

print("Generated homepage with book links.")

# --- 2) Generate book pages and poem pages ---
for book in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book)
    if not os.path.isdir(book_path):
        continue

    book_display_name = book.replace("_", " ")
    book_output_dir = os.path.join(OUTPUT_DIR, book)
    os.makedirs(book_output_dir, exist_ok=True)

    poem_links = []  # store links to poems for the book page

    # There should be only one txt file per book
    for filename in sorted(os.listdir(book_path)):
        if filename.endswith(".txt"):
            poem_path = os.path.join(book_path, filename)
            with open(poem_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if not lines:
                    continue
                title = lines[0].replace("Title: ", "").strip()
                content = "\n".join(lines[1:]).strip()

            # Generate poem page inside book directory
            poem_file_name = f"{os.path.splitext(filename)[0]}.html"
            poem_file = os.path.join(book_output_dir, poem_file_name)

            poem_html = (
                f"<h2>{title}</h2>\n"
                f"<div class='poem-box'>{content}</div>\n"
                f"<p><a href='{book}.html'>← Back to {book_display_name}</a></p>"
            )

            with open(poem_file, "w", encoding="utf-8") as f:
                f.write(template.replace("{poems_html}", poem_html))

            # Add link for book page
            poem_links.append((title, poem_file_name))

    # Generate the main book page inside the book directory
    book_page_html = f"<h1>{book_display_name}</h1>\n<ul>\n"
    for title, link in poem_links:
        book_page_html += f"<li><a href='{link}'>{title}</a></li>\n"
    book_page_html += "</ul>\n<p><a href='../index.html'>← Back to main page</a></p>"

    book_page_file = os.path.join(book_output_dir, f"{book}.html")
    with open(book_page_file, "w", encoding="utf-8") as f:
        f.write(template.replace("{poems_html}", book_page_html))

    print(f"Generated book '{book}' with its poem pages.")
