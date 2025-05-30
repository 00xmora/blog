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

# Extracts frontmatter and content from a Markdown file
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

# Generate index.md for all folders inside content_dir
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
            image = frontmatter.get("image", "/assets/images/default.png")
            summary = frontmatter.get("summary", "")

            # Parse date for sorting
            try:
                sort_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                sort_date = datetime.min

            cards.append({
                "html": card_template.format(
                    link=filename,
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

# Run the generator
generate_index_files(content_dir)

print("✅ All index.md files updated with cards.")
