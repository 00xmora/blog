import os
import yaml
from datetime import datetime

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

            # Other metadata
            date_str = frontmatter.get("date", "")
            # Use generated social card as default image
            filename_base = os.path.splitext(filename)[0]
            default_image = f"/assets/images/social/{filename_base}.png"
            image = frontmatter.get("image", default_image)
            summary = frontmatter.get("summary", "")

            # Parse date for sorting
            try:
                sort_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                sort_date = datetime.min

            # Make link path: /folder/filename/ (without .md)
            relative_path = os.path.relpath(filepath, base_dir)
            link = "/" + os.path.splitext(relative_path)[0] + "/"
            link = link.replace("\\", "/")  # for Windows compatibility

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
        output_html = '<div class="md-grid">\n' + "\n".join(card["html"] for card in cards) + '\n</div>\n'

        # Write the index.md
        index_path = os.path.join(root, index_filename)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(root).capitalize()}\n\n")
            f.write(output_html)

# Run it
generate_index_files(content_dir)

print("✅ All index.md files updated with correct links.")
