from flask import Flask, render_template, abort, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path
from feedgen.feed import FeedGenerator

import markdown
import frontmatter

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)

BLOG_DIR = Path("blog")

md = markdown.Markdown(
    extensions=[
        "fenced_code",
        "tables"
    ]
)

def get_posts():

    posts = []

    for file in BLOG_DIR.glob("*.md"):

        post = frontmatter.load(file)

        slug = file.name[:-3] 

        post_tags = post.get('tags', [])
        if isinstance(post_tags, str):
            post_tags = [t.strip() for t in post_tags.split(',')]

        posts.append({
            "slug": file.stem,
            "title": post.get("title", file.stem),
            "date": post.get("date", ""),
            "updated": post.get("updated",""),
            "description": post.get("description", ""),
            "url": f'https://blog.ammayti.com/{slug}',
            "tags": post_tags
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

@app.route('/feed')
@app.route('/rss')
def rss_feed():
    fg = FeedGenerator()
    fg.title('Pradyumna Shenvi\'s Blog')
    fg.link(href='https://blog.ammayti.com', rel='alternate')
    fg.description('Tech, Fiction and Musings.')

    posts = get_posts()

    for post in posts:
        fe = fg.add_entry()
        fe.title(post['title'])
        fe.link(href=post['url'])
        fe.description(post['description'])
        if post['date']:
            fe.pubDate(post['date'])

         if post['tags']:
            fe.category([{'term': tag} for tag in post['tags']])

    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


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
        updated=post.get("updated","")
        description=post.get("description","")
        content=html
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080
    )