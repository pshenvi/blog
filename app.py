from flask import Flask, render_template, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path

import markdown
import frontmatter

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)

CONTENT_DIR = Path("content")

md = markdown.Markdown(
    extensions=[
        "fenced_code",
        "tables"
    ]
)

def get_posts():

    posts = []

    for file in CONTENT_DIR.glob("*.md"):

        post = frontmatter.load(file)

        posts.append({
            "slug": file.stem,
            "title": post.get("title", file.stem),
            "date": post.get("date", "")
            "updated": post.get("updated","")
        })

    posts.sort(
        key=lambda x: str(x["date"]),
        reverse=True
    )

    return posts


@app.route("/")
def index():

    posts = get_posts()

    return render_template(
        "index.html",
        posts=posts
    )


@app.route("/<slug>")
def blog_post(slug):

    path = CONTENT_DIR / f"{slug}.md"

    if not path.exists():
        abort(404)

    post = frontmatter.load(path)

    html = md.convert(post.content)
    md.reset()

    return render_template(
        "post.html",
        title=post.get("title", slug),
        date=post.get("date", ""),
        content=html
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080
    )