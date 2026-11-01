from tools.article_reader import read_article


url = (
    "https://research.google/blog/"
    "open-and-emergent-problems-in-agentic-"
    "privacy-and-security-a-contextual-angle/"
)

content = read_article(url)

print("Characters retrieved:", len(content))
print()
print(content[:1000])