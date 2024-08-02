from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.secret_key = 'vanilla'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(99), unique=True)
    password = db.Column(db.String(99))
    fName = db.Column(db.String(99))
    lName = db.Column(db.String(99))
    bio = db.Column(db.String(999), default = '')
    pfp = db.Column(db.String(99), nullable=False, default='default.jpg')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, default= '')
    created = db.Column(db.DateTime)
    author = db.Column(db.String(99))
    authorpfp = db.Column(db.String(99), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    content = db.Column(db.Text, default= '')
    author = db.Column(db.String(99))
    originalPost = db.Column(db.Integer)

@login_manager.user_loader
def loader_user(user_id):
    return user.query.get(user_id)

@app.route('/', methods=["GET", "POST"])

def index():
    db.create_all()

    posts = Post.query.all()

    if request.method == "POST":
        username = request.form.get('search')
        print(username)
        posts = Post.query.filter_by(author = username).all()


    return render_template ('index.html', posts=posts)

@app.route('/login', methods=['post', 'get'])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        login = user.query.filter_by(username = username, password = password).first()

        print(login)

        if login is not None:
            login_user(login)
            return redirect(url_for('secretpage'))
        
    return render_template ('login.html')

@app.route('/signup', methods=['post', 'get'])
def signup():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        eightCharacters = False

        if len(password) < 8:
            message += " Have eight characters! "
        else:
            eightCharacters = True

        if password != cpassword:
            print("No match!")
            message = "Passwords do not match!"

        if eightCharacters == True:
            if password == cpassword:
                registration = user(fName = firstname, lName = lastname, username = username, password = password)
                db.session.add(registration)
                db.session.commit()

                return redirect(url_for('thankyou'))

    return render_template('signup.html', message = message)


@app.route('/profile', methods=['post', 'get'])
def profile():
    image_file = url_for('static', filename='pfps/' + current_user.pfp)
    bio = current_user.bio
    print(image_file)

    if request.method == 'POST':
        f = request.files['avatar']

        if f.filename is not '':
            currentPhoto = current_user.username + ".jpg"
            f.save('static/pfps/' + currentPhoto)
            current_user.pfp = currentPhoto
        
        current_user.bio = request.form.get('bio')
        db.session.commit()

    return render_template('profile.html', image_file=image_file, bio=bio)

@app.route('/post/new', methods=['post', 'get'])
@login_required
def new_post():
    post = Post(content = request.form.get('content'), author= current_user.username, created= datetime.now(), authorpfp = current_user.pfp)
    
    print(request.form.get('content'))

    if request.form.get('content') != '' and request.form.get('content') is not None:
        db.session.add(post)
        db.session.commit()


    return render_template('create_post.html', post=post)

@app.route('/post/<int:post_id>', methods=['post', 'get'])
def view_post(post_id):
    posts = Post.select().where(Post.id == post_id)
    return render_template('postfeed.html', feed = posts)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/secretpage')
def secretpage():
    return render_template('secretpage.html')

@app.route('/signout')
def signout():
    logout_user()
    return render_template('signout.html')


if __name__ == '__main__':
    app.run(debug=True)