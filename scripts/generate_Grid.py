import os
import yaml
from datetime import datetime
import re

content_dir = "docs"
index_filename = "index.md"

# New template: Simple list without images
list_template = """
<div class="article-list">
  <a href="{link}" class="article-link">
    <h3>{title}</h3>
    <div class="article-meta">
      <span class="read-time">{read_time}</span>
      <span class="publish-date">Published: {date}</span>
    </div>
    <p class="article-excerpt">{summary}</p>
  </a>
</div>
"""

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

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
        # Skip directories without markdown files (except for their own index.md)
        md_files = [f for f in files if f.endswith(".md") and f != index_filename]
        if not md_files and not any(d for d in dirs if os.path.exists(os.path.join(root, d, index_filename))):
            continue

        items = []

        # Process subdirectories first (for nested structure)
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            dir_index = os.path.join(dirpath, index_filename)
            
            if os.path.exists(dir_index):
                frontmatter, _ = extract_frontmatter(dir_index)
                title = frontmatter.get("title", dirname.replace("-", " ").title())
                date = frontmatter.get("date", "")
                summary = frontmatter.get("summary", f"Articles about {title}")
                read_time = frontmatter.get("read_time", "")
                relative_path = os.path.relpath(dirpath, base_dir).replace("\\", "/")
                items.append({
                    "html": list_template.format(
                        link = f"/{relative_path}/",
                        title=title,
                        read_time=read_time,
                        date=date,
                        summary=summary
                    ),
                    "sort_date": datetime.combine(date, datetime.min.time()) if isinstance(date, datetime.date) else (
                    datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) and date else datetime.min
                    )

                })

        # Process markdown files
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
                    title = os.path.splitext(filename)[0].replace("-", " ").title()

            # Metadata
            date_str = frontmatter.get("date", "")
            summary = frontmatter.get("summary", "")
            read_time = frontmatter.get("read_time", "")

            # Make link path
            relative_path = os.path.relpath(filepath, base_dir)
            filename_base = slugify(os.path.splitext(filename)[0])
            folder = os.path.dirname(relative_path).replace("\\", "/")
            link = "/" + (folder + "/" if folder else "") + filename_base + "/"

            try:
                sort_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                sort_date = datetime.min

            items.append({
                "html": list_template.format(
                    link=link,
                    title=title,
                    read_time=read_time,
                    date=date_str,
                    summary=summary
                ),
                "sort_date": sort_date
            })

        # Sort by date (newest first)
        items.sort(key=lambda x: x["sort_date"], reverse=True)
        items_html = '<div class="article-container">\n' + "\n".join(item["html"] for item in items) + '\n</div>'

        # Update index.md
        start_marker = "<!-- ARTICLES:START -->"
        end_marker = "<!-- ARTICLES:END -->"
        index_path = os.path.join(root, index_filename)

        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            if start_marker in existing_content and end_marker in existing_content:
                new_content = existing_content.replace(
                    f"{start_marker}.*?{end_marker}",
                    f"{start_marker}\n{items_html}\n{end_marker}",
                    flags=re.DOTALL
                )
            else:
                new_content = f"# {os.path.basename(root).capitalize()}\n\n{start_marker}\n{items_html}\n{end_marker}\n"
        else:
            new_content = f"# {os.path.basename(root).capitalize()}\n\n{start_marker}\n{items_html}\n{end_marker}\n"

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

generate_index_files(content_dir)
print("✅ Article lists generated successfully.")