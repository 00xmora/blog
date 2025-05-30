import os
from datetime import datetime

# المسارات اللي هنولد فيها index
sections = ['docs/writeups', 'docs/research']

for section in sections:
    posts = []
    for file in os.listdir(section):
        path = os.path.join(section, file)
        if file.endswith(".md") and file != "index.md":
            # نحاول نقرأ التاريخ من frontmatter أو اسم الملف (لو فيه)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                title = file.replace(".md", "").replace("-", " ").title()
                date = None
                for line in lines:
                    if line.strip().startswith("date:"):
                        try:
                            date = datetime.strptime(line.strip().split(":", 1)[1].strip(), "%Y-%m-%d")
                        except:
                            pass
                    if line.strip().startswith("# "):  # أول عنوان
                        title = line.strip()[2:]
                        break
                posts.append({
                    "file": file,
                    "title": title,
                    "date": date or datetime.min
                })

    # ترتيب حسب التاريخ
    posts.sort(key=lambda x: x["date"], reverse=True)

    # بناء محتوى الـ index.md
    index_content = f"# {section.split('/')[-1].capitalize()}\n\n<div class=\"md-grid\">\n\n"
    for post in posts:
        index_content += f"""<div class="md-grid-item">
### [{post['title']}]({post['file']})
</div>\n\n"""
    index_content += "</div>\n"

    # كتابة الملف
    with open(os.path.join(section, "index.md"), "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"✅ Generated: {section}/index.md")
