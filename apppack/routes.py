import os
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, flash, abort
from apppack import app, db, bcrypt, mail
from apppack.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestRestForm, ResetPasswordForm
from apppack.models import User, Post, Todo
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route('/base/')
def base():
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('base.html', image_file=image_file)

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
   

@app.route("/post/<int:post_id>/update", methods=['POST', 'GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    forms = PostForm()
    if forms.validate_on_submit():
        post.title = forms.title.data
        post.content = forms.content.data
        db.session.commit()
        flash('Yourpost has been updated')
        return redirect(url_for('post', post_id=post.id))
    forms.title.data = post.title
    forms.content.data = post.content

    return render_template('update_post.html', forms=forms)

@app.route("/post/<int:post_id>/delete", methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted")
    return redirect('/')

@app.route("/user/<username>", methods=['POST', 'GET'])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('userposts.html', posts=posts, post=post, user=user, image_file=image_file)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='jqlabweb@gmail.com', recipients=[user.email])
    msg = f'''
    To reset your password, visit the following link:
    
    {url_for('reset_token', token=token, _external=True )}

    If you did not make this request then simply ignore this email
    
    '''





@app.route("/reset_password", methods=['POST', 'GET')]
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    forms = RequestRestForm()
    if forms.validate_on_submit():
        user = User.query.filter_by(email=forms.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your pasword')
        return redirect('/login/')
    return render render_template('reset_request.html', forms=forms)


@app.route("/reset_password/<token>", methods=['POST', 'GET')]
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('/')
    user = User.verify_reset_token(token):
    if user is None:
        flash('That is an invalid or expired token. Please try again')
    forms = ResetPasswordForm()
    return render_template('reset_token.html', forms=forms)
