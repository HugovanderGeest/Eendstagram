from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
import secrets
from PIL import Image

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def save_post(filename, caption):
    posts = []
    if os.path.exists('posts.json'):
        with open('posts.json', 'r') as f:
            posts = json.load(f)
    # Add the new post to the list
    posts.append({
        'filename': filename,
        'caption': caption,
        'likes': 0,
        'comments': []
    })
    # Save the posts back to the JSON file
    with open('posts.json', 'w') as f:
        json.dump(posts, f)

@app.route('/')
def index():
    # Load the posts from the JSON file
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    # Reverse the list of posts
    posts = posts[::-1]
    return render_template('index.html', posts=posts)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        filename = request.form.get('filename')  # Get filename from form data
        if password == 'iksisknap':
            # Load the posts from the JSON file
            with open('posts.json', 'r') as f:
                posts = json.load(f)
            # Remove the post with the given filename
            posts = [post for post in posts if post['filename'] != filename]
            # Save the posts back to the JSON file
            with open('posts.json', 'w') as f:
                json.dump(posts, f)
            return render_template('admin.html', posts=posts)
        else:
            return redirect("/admin")
    else:
        return render_template('login.html')
    

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        caption = request.form.get('caption')
        description = request.form.get('description')
        photo = request.files.get('photo')
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('static/uploads', filename)
            photo.save(photo_path)

            # Remove the call to is_duck

            # Open the image file
            img = Image.open(photo_path)
            # Resize it - keeping aspect ratio
            max_size = (1080, 1080)
            img.thumbnail(max_size)
            # Save it back to the same path
            img.save(photo_path, optimize=True, quality=85)

            save_post(filename, caption, description)
            return redirect(url_for('index'))
    return render_template('upload.html')
    

def save_post(filename, caption, description):
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    posts.append({
        'filename': filename,
        'caption': caption,
        'description': description,
        'likes': 0,
        'comments': []
    })
    with open('posts.json', 'w') as f:
        json.dump(posts, f)

@app.route('/posts')
def posts():
    # Load the posts from the JSON file
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    return render_template('posts.html', posts=posts)

@app.route('/like', methods=['POST'])
def like():
    data = request.get_json()
    filename = data['filename']
    # Check if the user has already liked this post
    if 'liked_posts' in session and filename in session['liked_posts']:
        return json.dumps({'message': 'You have already liked this post.'}), 400
    # Load the posts from the JSON file
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    # Increment the likes for the post with the given filename
    for post in posts:
        if post['filename'] == filename:
            post['likes'] += 1
            updated_likes = post['likes']
    # Save the posts back to the JSON file
    with open('posts.json', 'w') as f:
        json.dump(posts, f)
    # Add this post to the list of posts the user has liked
    if 'liked_posts' not in session:
        session['liked_posts'] = []
    session['liked_posts'].append(filename)
    return json.dumps({'likes': updated_likes}), 200

@app.route('/comment', methods=['POST'])
def comment():
    data = request.get_json()
    filename = data['filename']
    comment = data['comment']
    # Load the posts from the JSON file
    with open('posts.json', 'r') as f:
        posts = json.load(f)
    # Add the comment to the post with the given filename
    for post in posts:
        if post['filename'] == filename:
            post['comments'].append(comment)
    # Save the posts back to the JSON file
    with open('posts.json', 'w') as f:
        json.dump(posts, f)
    return json.dumps({'message': 'Comment added.'}), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Save the user data to a JSON file
        users = []
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                users = json.load(f)
        users.append({'username': username, 'password': password})
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('index'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)