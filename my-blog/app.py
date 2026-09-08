from flask import Flask, render_template, request, redirect, url_for
import os
import json
import html
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, 'posts')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

CATEGORIES = [
    'Food', 'Craft', 'Music', 'Life', 'Culture',
    'Travel', 'Opinion', 'Books', 'Beauty & Style', 'Wellness'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_posts():
    posts = []
    if os.path.exists(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(POSTS_DIR, filename)
                with open(filepath, 'r') as f:
                    post = json.load(f)
                    posts.append(post)
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts

@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<slug>')
def post(slug):
    filepath = os.path.join(POSTS_DIR, slug + '.json')
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            post = json.load(f)
        return render_template('post.html', post=post)
    return "Post not found", 404

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/categories')
def categories():
    posts = get_posts()
    selected = request.args.get('cat', None)
    if selected:
        posts = [p for p in posts if p.get('category') == selected]
    return render_template('categories.html', posts=posts, categories=CATEGORIES, selected=selected)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {'error': 'No image'}, 400
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return {'url': f'/static/uploads/{filename}'}
    return {'error': 'Invalid file'}, 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        title = request.form.get('title')
        content = html.unescape(request.form.get('content', ''))
        category = request.form.get('category')
        date = datetime.now().strftime('%B %d, %Y')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        slug = title.lower().strip().replace(' ', '-').replace("'", '').replace(',', '')
        slug = f"{slug}-{timestamp}"

        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                img_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{img_timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                cover_image = f'/static/uploads/{filename}'

        post = {
            'title': title,
            'content': content,
            'category': category,
            'date': date,
            'slug': slug,
            'cover_image': cover_image
        }

        post_filepath = os.path.join(POSTS_DIR, slug + '.json')
        with open(post_filepath, 'w') as f:
            json.dump(post, f)

        return redirect(url_for('index'))
    return render_template('admin.html', categories=CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)
