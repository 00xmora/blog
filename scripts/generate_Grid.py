import os
from datetime import datetime
import re

# Base content directory
content_dir = "docs"
index_filename = "index.md"

# Template for each card
card_template = """
<div class="card">
  <a href="{link}">
    {image_tag}
    <div class="card-body">
      <strong>{title}</strong><br>
      <small>{date}</small>
      <p>{summary}</p>
    </div>
  </a>
</div>
"""

# Default image for folders if not specified in their index.md
default_folder_image = "/assets/images/folder.png" 

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.lower() # Ensure slug is lowercase

def humanize_folder_name(folder_name):
    return folder_name.replace('-', ' ').title()

# Extract content from markdown file, ignoring frontmatter
def extract_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            full_content = f.read()
            # Try to skip frontmatter if present (lines between ---)
            parts = full_content.split('---', 2)
            if len(parts) > 2:
                content = parts[2].strip() # Content after the second ---
            else:
                content = full_content.strip() # No frontmatter or incomplete frontmatter
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""
    return content

# Generate HTML for index cards
def generate_index_files(base_dir):
    # Walk through all directories starting from base_dir
    for root, dirs, files in os.walk(base_dir):
        cards = []

        # 1. Process Markdown files directly in the current directory
        md_files = [f for f in files if f.endswith(".md") and f != index_filename]
        for filename in md_files:
            filepath = os.path.join(root, filename)
            content = extract_content(filepath)

            # Try to extract title from H1 tag in content
            title = ""
            h1_match = re.search(r'#\s*(.+)', content)
            if h1_match:
                title = h1_match.group(1).strip()
            if not title:
                title = os.path.splitext(filename)[0].replace('-', ' ').title() # Fallback to filename

            # Extract first paragraph for summary
            summary = ""
            first_paragraph_match = re.search(r'([^\n]+)', content.strip())
            if first_paragraph_match:
                summary = first_paragraph_match.group(1).strip()
                if len(summary) > 150: 
                    summary = summary[:150] + "..."

            # Date cannot be reliably extracted without YAML. Omit from display.
            date_str = "" 
            # Use file modification time for sorting if date is not available
            try:
                file_mod_time = os.path.getmtime(filepath)
                sort_date = datetime.fromtimestamp(file_mod_time)
            except Exception:
                sort_date = datetime.min 

            filename_base_slug = slugify(os.path.splitext(filename)[0])
            folder_path_for_image = os.path.relpath(root, base_dir).replace("\\", "/") # Relative path from 'docs'
            if folder_path_for_image == ".": # If root is 'docs' itself
                folder_slug_for_image = "" 
            else:
                folder_slug_for_image = slugify(folder_path_for_image)

            # Construct default image path based on filename slug and folder slug
            # Assuming social images are structured under /assets/images/social/<folder_slug>/<filename_slug>.png
            image = f"/assets/images/social/{folder_slug_for_image}/{filename_base_slug}.png" if folder_slug_for_image else f"/assets/images/social/{filename_base_slug}.png"

            image_tag = f'<img src="{image}" alt="{title}">' # Always try to include an image tag

            relative_path = os.path.relpath(filepath, base_dir)
            link = "/" + relative_path.replace("\\", "/")
            link = os.path.splitext(link)[0] + "/" # Ensure trailing slash for MkDocs

            cards.append({
                "html": card_template.format(
                    link=link,
                    image_tag=image_tag,
                    title=title,
                    date=date_str,
                    summary=summary
                ),
                "sort_date": sort_date
            })

        # 2. Process Subdirectories directly in the current directory
        for dirname in dirs:
            # Exclude hidden directories (e.g., .git, .github) and assets folders
            if dirname.startswith('.') or dirname == "assets": 
                continue

            folder_path_abs = os.path.join(root, dirname)
            folder_index_path = os.path.join(folder_path_abs, index_filename)

            # Only create a card for a folder if it contains an index.md
            if not os.path.exists(folder_index_path):
                continue

            # For folders, we rely on the humanized name and a generic description/image
            folder_title = humanize_folder_name(dirname)
            folder_description = f"Explore content in {folder_title}."
            
            # Use default folder image as we cannot parse frontmatter for specific image
            image_tag = f'<img src="{default_folder_image}" alt="{folder_title}">' 

            relative_folder_path = os.path.relpath(folder_path_abs, base_dir)
            folder_link = "/" + relative_folder_path.replace("\\", "/") + "/"

            # Use modification date of the folder's index.md for sorting
            try:
                folder_mod_time = os.path.getmtime(folder_index_path)
                folder_sort_date = datetime.fromtimestamp(folder_mod_time)
            except Exception:
                folder_sort_date = datetime.min # If error, place at end

            cards.append({
                "html": card_template.format(
                    link=folder_link,
                    image_tag=image_tag,
                    title=folder_title,
                    date="", # No specific date displayed for folder cards
                    summary=folder_description
                ),
                "sort_date": folder_sort_date
            })

        # Sort all collected cards (files and folders) by date descending
        cards.sort(key=lambda x: x["sort_date"], reverse=True)
        cards_html = '<div class="md-grid">\n' + "\n".join(card["html"] for card in cards) + '\n</div>\n'

        # Update the index.md file in the current directory
        start_marker = ""
        end_marker = ""

        index_path = os.path.join(root, index_filename)

        # Read existing content or create new if index.md doesn't exist
        existing_content = ""
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        if start_marker in existing_content and end_marker in existing_content:
            # Use find and slicing instead of split to avoid 'empty separator' ValueError
            start_index = existing_content.find(start_marker)
            end_index = existing_content.find(end_marker)

            before = existing_content[:start_index]
            after = existing_content[end_index + len(end_marker):]
            new_content = f"{before}{start_marker}\n{cards_html}\n{end_marker}{after}"
        else:
            # If markers not found, either add them or create a new file
            # If it's an existing file without markers, assume we add them at the end.
            # If it's a new index file, start with a default title and markers.
            if not existing_content.strip(): # Check if file is essentially empty
                new_content = f"# {os.path.basename(root).replace('-', ' ').title()}\n\n{start_marker}\n{cards_html}\n{end_marker}\n"
            else: # Existing content but no markers, append
                 new_content = f"{existing_content}\n{start_marker}\n{cards_html}\n{end_marker}\n"


        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Run the generation script
generate_index_files(content_dir)