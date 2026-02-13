from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ DATABASE MODELS ------------------

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='blogs')

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    search = request.args.get('search')
    category_id = request.args.get('category')

    blogs = Blog.query

    if search:
        blogs = blogs.filter(Blog.title.contains(search))

    if category_id:
        blogs = blogs.filter_by(category_id=category_id)

    blogs = blogs.all()
    categories = Category.query.all()

    return render_template('home.html', blogs=blogs, categories=categories)

@app.route('/post/<int:id>')
def view_post(id):
    blog = Blog.query.get_or_404(id)
    return render_template('view_post.html', blog=blog)

# -------- ADMIN ROUTES --------

@app.route('/add', methods=['GET', 'POST'])
def add_post():
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        category_id = request.form['category']

        new_blog = Blog(
            title=title,
            content=content,
            author=author,
            category_id=category_id
        )

        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_post.html', categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    blog = Blog.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        blog.title = request.form['title']
        blog.content = request.form['content']
        blog.author = request.form['author']
        blog.category_id = request.form['category']

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit_post.html', blog=blog, categories=categories)

@app.route('/delete/<int:id>')
def delete_post(id):
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('home'))

# -------- CREATE DATABASE --------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


