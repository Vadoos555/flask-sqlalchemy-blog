from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegisterForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse


@app.route('/')
def index():
    posts = Post.query.order_by(Post.id).all()

    return render_template('index.html', title='Homepage', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user or login')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        form.validate_new_user()
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are registered on website')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not body:
            flash('Post can not be empty')
            return redirect(url_for('add_post'))

        post = Post(title=title, body=body)
        try:
            db.session.add(post)
            db.session.commit()
        except:
            flash('Error adding post to DB')

        flash('Your post is published.')
        return redirect(url_for('index'))

    return render_template('add_post.html', title='Add post')


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def show_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if request.method == 'POST':
        if post.author != current_user:
            flash('Вы не можете удалить это сообщение!')
            return redirect(url_for('index'))

        try:
            db.session.delete(post)
            db.session.commit()
            flash('Ваше сообщение было удалено!')
            return redirect(url_for('index'))
        except:
            flash('Error removing post from DB')

    return render_template('show_post.html', title='show post', post=post)
