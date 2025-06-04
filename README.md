# Omar Samy | Cybersecurity Blog

<p align="center">
  <img alt="Cybersecurity Banner" src="https://00xmora.github.io/assets/images/social_logo.png" width="600">
</p>

Welcome to the repository for my personal blog, hosted at [https://00xmora.github.io/](https://00xmora.github.io/). This blog is a space to share my findings, research, and practical experience in cybersecurity, focusing on penetration testing, bug bounty, capture-the-flag (CTF) challenges, and more. The site is built using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Features

- **Cybersecurity Content**: Writeups on web security, bug bounty, CTFs, and penetration testing techniques.
- **Technical Guides**: Notes from courses, certifications, and curated cheatsheets.
- **Projects & Experiments**: Documentation of home lab setups and cybersecurity projects.
- **Responsive Design**: Built with Material for MkDocs for a clean, mobile-friendly experience.
- **Search Functionality**: Easy navigation through blog content.

## Prerequisites

To run or contribute to this blog locally, ensure you have the following installed:
- [Python](https://www.python.org/) (version 3.7 or higher)
- [MkDocs](https://www.mkdocs.org/) with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Git](https://git-scm.com/)

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/00xmora/00xmora.github.io.git
   cd 00xmora.github.io
   ```

2. **Install Dependencies**:
   Install MkDocs and Material for MkDocs:
   ```bash
   pip install mkdocs mkdocs-material
   ```

3. **Run Locally**:
   Start the development server:
   ```bash
   mkdocs serve
   ```
   Open your browser to `http://localhost:8000` to preview the blog.

4. **Deploy**:
   Build the site and push to the `gh-pages` branch:
   ```bash
   mkdocs gh-deploy
   ```
   The site will be deployed to https://00xmora.github.io/.

## Project Structure

```
00xmora.github.io/
├── docs/                 # Markdown files for blog content
│   ├── writeups/         # Blog posts for CTF and bug bounty writeups
│   ├── research/         # Research and technical guides
│   └── about.md          # About page content
├── mkdocs.yml            # MkDocs configuration file
├── assets/               # Static assets (images, CSS, JS)
└── README.md             # This file
```

## Contributing

Contributions are welcome, especially for improving writeups, adding new content, or enhancing the site’s design. To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Add or edit Markdown files in the `docs/` directory or modify the theme in `mkdocs.yml`.
4. Commit your changes (`git commit -m "Add your feature"`).
5. Push to your branch (`git push origin feature/your-feature`).
6. Open a pull request.

Please ensure your contributions align with the blog’s focus on cybersecurity and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

Reach out to me on [X (Twitter)](https://x.com/your-username) or via email at [your-email@example.com] for questions, feedback, or collaboration.