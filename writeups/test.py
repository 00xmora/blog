import frontmatter

post = frontmatter.load("How-a-CORS-Misconfiguration-Let-Me-Steal-auth-Tokens.md")
print(post.metadata)
