from NewsApp.models import User
from NewsApp import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from NewsApp.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchBarForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os, math, json
from PIL import Image
from NewsApp.api_consumer import NewsApiParser

x = ""
y = ""
url_to_hit = ""


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    global x
    global y
    global url_to_hit
    form = SearchBarForm()
    rule = request.url_rule
    if request.method == 'POST':
        x = form.keywords.data
        y = form.year.data
    elif request.method == 'GET':
        print(rule)
        if 'home' in str(rule):
            print("bhava")
            x = ""
            y = ""
        form.keywords.data = x
        form.year.data = y

    num_of_posts: int = 3
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.filter_by().all()
    url_to_hit = "https://chroniclingamerica.loc.gov/search/titles/results/?&format=json"

    if form.year.data is None:
        form.year.data = ""
    if form.keywords.data is None:
        form.keywords.data = ""

    if form.year.data == "" and form.keywords.data == "":
        pass
    else:
        url_to_hit = "https://chroniclingamerica.loc.gov/search/pages/results/?&state=&date1={}&date2={}&proxtext={}&dateFilterType=yearRange&rows=50&searchType=basic&format=json".format(
            form.year.data, form.year.data, form.keywords.data)

    # flash(url_to_hit, "success")
    news = NewsApiParser(url_to_hit)
    all_data = news.getAllData()
    posts = all_data['items']

    last: int = math.ceil(len(posts) / num_of_posts)
    print(len(posts))
    print("Value of last"+str(last))
    posts = posts[(page - 1) * num_of_posts:(page - 1) * num_of_posts + num_of_posts]
    # print(posts)
    if not last in [0,1]:
        if page == 1:
            prev = "#"
            next = "/?page=" + str(page + 1)
        elif page == last:
            prev = "/?page=" + str(page - 1)
            next = "#"
        else:
            prev = "/?page=" + str(page - 1)
            next = "/?page=" + str(page + 1)
    else:
        prev = "#"
        next = "#"

    return render_template("home.html", posts=posts, prev=prev, next=next, page=page, last=last, form=form)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your Account has been created! Now you can Log in", "success")
        return redirect(url_for('login'))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash("Login Failed. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics/', picture_fn)

    output_size = (125, 125)
    compressed_pic = Image.open(form_picture)
    compressed_pic.thumbnail(output_size)
    compressed_pic.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your Account has been updated")
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", form=form, image_file=image_file)


@app.route("/post/<post_id>")
def post(post_id):
    print(post_id)
    # post = Post.query.get_or_404(post_id)
    news = NewsApiParser(url_to_hit)
    all_data = news.getAllData()
    post = None
    for post in all_data['items']:
        if post['lccn'] == post_id:
            post = post
            break
    if post is not None:
        # post = json.dumps(post, sort_keys=True, indent=4, separators=(',', ': '))
        return render_template('post.html', post=post)
    else:
        abort(404)
