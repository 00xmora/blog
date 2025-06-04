import os
import yaml
from datetime import datetime
import re

# Base content directory
content_dir = "docs"
index_filename = "index.md"

# Template for each card
card_template = """
<div class="card">
  <a href="{link}">
    <img src="{image}" alt="{title}">
    <div class="card-body">
      <strong>{title}</strong><br>
      <small>{date}</small>
      <p>{summary}</p>
    </div>
  </a>
</div>
"""

def slugify(text):
    # تحول النص لـ lowercase
    text = text.lower()
    # تشيل أي حاجة مش حرف أو رقم أو مسافة
    text = re.sub(r'[^\w\s-]', '', text)
    # تستبدل المسافات والـ _ بـ "-"
    text = re.sub(r'[\s_]+', '-', text)
    return text




# Extract frontmatter from markdown file
def extract_frontmatter(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read().split('---')
            if len(lines) >= 3:
                frontmatter = yaml.safe_load(lines[1])
                content = lines[2].strip()
            else:
                frontmatter = {}
                content = lines[0].strip()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return {}, ""

    return frontmatter or {}, content

# Generate HTML for index cards
def generate_index_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        md_files = [f for f in files if f.endswith(".md") and f != index_filename]
        if not md_files:
            continue

        cards = []

        for filename in md_files:
            filepath = os.path.join(root, filename)
            frontmatter, content = extract_frontmatter(filepath)

            # Title logic
            title = frontmatter.get("title")
            if not title:
                for line in content.splitlines():
                    if line.strip().startswith("#"):
                        title = line.strip().lstrip("#").strip()
                        break
                if not title:
                    title = os.path.splitext(filename)[0]

            # Metadata
            date_str = frontmatter.get("date", "")
            summary = frontmatter.get("summary", "")

            filename_base = slugify(os.path.splitext(filename)[0])
            folder_slug = os.path.basename(os.path.dirname(filepath))
            default_image = f"/assets/images/social/{folder_slug}/{filename_base}.png"
            image = frontmatter.get("image", default_image)

            # Parse date for sorting
            try:
                sort_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                sort_date = datetime.min

            # Make link path
            relative_path = os.path.relpath(filepath, base_dir)
            filename_base = slugify(os.path.splitext(os.path.basename(filepath))[0])
            folder = os.path.dirname(relative_path).replace("\\", "/")
            link = "/" + (folder + "/" if folder else "") + filename_base + "/"
            link = link.replace("\\", "/")
            cards.append({
                "html": card_template.format(
                    link=link,
                    image=image,
                    title=title,
                    date=date_str,
                    summary=summary
                ),
                "sort_date": sort_date
            })

        # Sort cards by date descending
        cards.sort(key=lambda x: x["sort_date"], reverse=True)
        cards_html = '<div class="md-grid">\n' + "\n".join(card["html"] for card in cards) + '\n</div>\n'

        # Markers
        start_marker = "<!-- CARDS:START -->"
        end_marker = "<!-- CARDS:END -->"

        index_path = os.path.join(root, index_filename)

        # If index exists, replace content between markers
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            if start_marker in existing_content and end_marker in existing_content:
                before = existing_content.split(start_marker)[0]
                after = existing_content.split(end_marker)[1]
                new_content = f"{before}{start_marker}\n{cards_html}\n{end_marker}{after}"
            else:
                # Markers not found — overwrite
                new_content = f"# {os.path.basename(root).capitalize()}\n\n{start_marker}\n{cards_html}\n{end_marker}\n"
        else:
            # No index file — create new one
            new_content = f"# {os.path.basename(root).capitalize()}\n\n{start_marker}\n{cards_html}\n{end_marker}\n"

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Run it
generate_index_files(content_dir)

print("✅ All index.md files updated with social cards.")
