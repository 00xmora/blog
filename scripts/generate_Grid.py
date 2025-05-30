import os
from datetime import datetime

ROOT_DIR = "docs"
MARKER_START = "<!-- POSTS_START -->"
MARKER_END = "<!-- POSTS_END -->"

def extract_post_metadata(path):
    title = os.path.basename(path).replace(".md", "").replace("-", " ").title()
    date = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    break
                line = lines[i].strip()
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("date:"):
                    try:
                        date = datetime.strptime(line.split(":", 1)[1].strip(), "%Y-%m-%d")
                    except:
                        pass

        for line in lines:
            if line.strip().startswith("# "):
                title = line.strip()[2:].strip()
                break

    return title, date or datetime.min

def update_index_for_directory(section_path):
    posts = []

    for file in os.listdir(section_path):
        full_path = os.path.join(section_path, file)
        if file.endswith(".md") and file != "index.md" and os.path.isfile(full_path):
            title, date = extract_post_metadata(full_path)
            posts.append({
                "file": file,
                "title": title,
                "date": date
            })

    if not posts:
        return

    posts.sort(key=lambda x: x["date"], reverse=True)

    cards_html = f"\n{MARKER_START}\n<div class=\"md-grid\">\n"
    for post in posts:
        cards_html += f"""<div class="md-grid-item">

### [{post['title']}]({post['file']})

</div>\n"""
    cards_html += "</div>\n" + MARKER_END + "\n"

    index_path = os.path.join(section_path, "index.md")

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if MARKER_START in content and MARKER_END in content:
            before = content.split(MARKER_START)[0]
            after = content.split(MARKER_END)[1]
            final = before + cards_html + after
        else:
            final = content.strip() + "\n\n" + cards_html
    else:
        folder_name = os.path.basename(section_path).capitalize()
        final = f"# {folder_name}\n\n{cards_html}"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(final)

    print(f"✅ Updated index.md for {section_path}")

# Loop on all folders in docs/
for folder in os.listdir(ROOT_DIR):
    section_path = os.path.join(ROOT_DIR, folder)
    if os.path.isdir(section_path):
        update_index_for_directory(section_path)
