import os

POEMS_DIR = "poems"           # contains subdirectories (books)
TEMPLATE_FILE = "templates/index_skeleton.html"
OUTPUT_DIR = "site"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read skeleton template
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

# --- 1) Generate main index.html ---
main_content = "<ul>\n"

for book_dir in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book_dir)
    if not os.path.isdir(book_path):
        continue
    display_name = book_dir.replace("_", " ")
    book_page = f"{book_dir}/{book_dir}.html"  # book page inside its folder
    main_content += f"<li><a href='{book_page}'>{display_name}</a></li>\n"

main_content += "</ul>\n"

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(template.replace("{poems_html}", main_content))

print("Generated main index.html with book links.")

# --- 2) Generate book pages and individual poem pages ---
for book_dir in sorted(os.listdir(POEMS_DIR)):
    book_path = os.path.join(POEMS_DIR, book_dir)
    if not os.path.isdir(book_path):
        continue

    display_name = book_dir.replace("_", " ")
    book_output_dir = os.path.join(OUTPUT_DIR, book_dir)
    os.makedirs(book_output_dir, exist_ok=True)

    book_content = f"<h1>{display_name}</h1>\n<ul>\n"

    # For each poem in the book
    for filename in sorted(os.listdir(book_path)):
        if filename.endswith(".txt"):
            poem_file_path = os.path.join(book_path, filename)
            with open(poem_file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if not lines:
                    continue
                title = lines[0].replace("Title: ", "").strip()
                content = "\n".join(lines[2:]).strip()  # skip title + blank line

                # Create a safe poem filename inside the book folder
                poem_slug = f"{os.path.splitext(filename)[0]}.html"
                poem_output_path = os.path.join(book_output_dir, poem_slug)

                # Generate individual poem page
                poem_html = f"<h1>{title}</h1>\n<pre>{content}</pre>\n"
                poem_html += f"<p><a href='{book_dir}.html'>← Back to {display_name}</a></p>"

                with open(poem_output_path, "w", encoding="utf-8") as pf:
                    pf.write(template.replace("{poems_html}", poem_html))

                # Add link to poem in the book page
                book_content += f"<li><a href='{poem_slug}'>{title}</a></li>\n"

    book_content += "</ul>\n"
    book_content += "<p><a href='../index.html'>← Back to main page</a></p>"

    # Generate book page inside the book folder
    book_page_path = os.path.join(book_output_dir, f"{book_dir}.html")
    with open(book_page_path, "w", encoding="utf-8") as f:
        f.write(template.replace("{poems_html}", book_content))

    print(f"Generated book page and poems for '{book_dir}'")
