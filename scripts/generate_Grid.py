import os
from datetime import datetime

sections = ['docs/writeups', 'docs/research']
marker_start = "<!-- POSTS_START -->"
marker_end = "<!-- POSTS_END -->"

for section in sections:
    posts = []
    for file in os.listdir(section):
        if file.endswith(".md") and file != "index.md":
            path = os.path.join(section, file)
            title = file.replace(".md", "").replace("-", " ").title()
            date = None

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                # لو فيه frontmatter
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

                # fallback: أول heading
                for line in lines:
                    if line.strip().startswith("# "):
                        title = line.strip()[2:].strip()
                        break

            posts.append({
                "file": file,
                "title": title,
                "date": date or datetime.min
            })

    posts.sort(key=lambda x: x["date"], reverse=True)

    # generate cards HTML
    cards_html = f"\n{marker_start}\n<div class=\"md-grid\">\n"
    for post in posts:
        cards_html += f"""<div class="md-grid-item">
### [{post['title']}]({post['file']})
</div>\n"""
    cards_html += "</div>\n" + marker_end + "\n"

    index_path = os.path.join(section, "index.md")

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if marker_start in content and marker_end in content:
            before = content.split(marker_start)[0]
            after = content.split(marker_end)[1]
            final = before + cards_html + after
        else:
            final = content.strip() + "\n\n" + cards_html
    else:
        final = f"# {section.split('/')[-1].capitalize()}\n\n" + cards_html

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(final)

    print(f"✅ Updated: {index_path}")
