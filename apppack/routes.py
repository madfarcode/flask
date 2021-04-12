import os
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, flash
from apppack import app, db, bcrypt
from apppack.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from apppack.models import User, Post, Todo
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/base/')
def base():
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('base.html', image_file=image_file)

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    posts = Post.query.all()
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('index.html', posts=posts, image_file=image_file)

@app.route('/about/')
def about():
    return render_template('about.html', name=name, lname=lname, age=age, country=country)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
       return 'Sorry but we have encouter some probleme deleting your post :('

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'An error occured ;)'
    
    else:
        return render_template('update.html', task=task)

@app.route('/Subscribe/', methods=['POST', 'GET'])
def subscribe():
    if current_user.is_authenticated:
        return redirect('/')
    forms = RegistrationForm()
    if request.method == 'POST':
        if forms.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(forms.password.data).decode('utf-8')
            user = User(username=forms.username.data, email=forms.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created, you are now able to Log in !','success')
            return redirect('/login/')
        else:
            flash(f"Account can't be created")
    return render_template('Subscribe.html', forms=forms)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    forms = LoginForm()
    if forms.validate_on_submit():
        user = User.query.filter_by(email=forms.email.data).first()
        if user and bcrypt.check_password_hash(user.password, forms.password.data):
            login_user(user, remember=forms.remember.data)
            return redirect('/')
        else:
            flash('Login unsuccessfull please check your email and password', 'danger')
    return render_template('login.html', forms=forms)

@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect('/')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn 


@app.route('/account/', methods=['POST', 'GET'])
@login_required
def account():
    forms = UpdateAccountForm()
    if forms.validate_on_submit():
        if forms.picture.data:
            picture_file = save_picture(forms.picture.data)
            current_user.image_file = picture_file
        current_user.username = forms.username.data
        current_user.email = forms.email.data
        db.session.commit()
        flash('Your account has been updated with success')
        return redirect('/account/')
    elif request.method == 'GET':
        forms.username.data = current_user.username
        forms.email.data = current_user.email
    return render_template('account.html', image_file=image_file, forms=forms)

@app.route('/post/new', methods=['POST', 'GET'])
@login_required
def post_new():
    image_file = url_for('static', filename='img/' + current_user.image_file)
    forms = PostForm()
    if forms.validate_on_submit():
        post = Post(title=forms.title.data, content=forms.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post HAs been created !' , 'success')
        return redirect('/')
    return render_template('create_post.html', forms=forms, image_file=image_file)