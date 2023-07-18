from flask import Flask, render_template, redirect, request
from prisma import Prisma, register
from prisma.models import User, Posts
from flask_login import login_user, current_user, logout_user
from libraries.db.models import UserModel, get_user
from flask_login import LoginManager
import hashlib

db = Prisma()
db.connect()
register(db)

app = Flask(__name__, template_folder='pages', static_folder='assets')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = "ABORT"


@app.login_manager.user_loader
def load_user(_id):
    if _id is not None:
      user = User.prisma().find_first(where={'id': _id})
      return user
    else:
      return None
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    if current_user.is_authenticated:
      return redirect('/dashboard')
    return render_template('login.html')

  if request.method == 'POST':
    data = request.form
    dk = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    data = {'email': data['username'], 'password': dk}
    if data is None:
      return render_template('login.html')
    user = get_user(data['email'])
    if user is None:
      return render_template('login.html')
    if user.password != dk:
      return render_template('login.html')
    login_user(UserModel(user))
    return redirect('/dashboard')

@app.route('/post')
def blog():
   post_id = request.args.getlist('post_id', type=int) 
   post = Posts.prisma().find_first(where={'id': post_id[0]})
   author = User.prisma().find_first(where={'id': post.authorId})
   return render_template('blog_post.html', post = post, author=author.name)

@app.route('/logout')
def logout():
   logout_user()
   return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
       return redirect('/login')

    post_count = Posts.prisma().count()
    if post_count == 1:
       post_count = 2
    else:
       post_count += 1
    last_post = Posts.prisma().find_first(where={'id': post_count - 1})
    print(last_post)
    return render_template('dashboard.html', post_count=post_count - 1, last_post=last_post)

@app.route('/new_post')
def new_post():
  if not current_user.is_authenticated:
    return redirect('/login')
  return render_template('create_post.html')

@app.route('/search', methods=['POST'])
def search():
  if request.method == 'POST':
    data = request.form
    posts = Posts.prisma().find_many(where={'title': {'contains': data['search']}})
    if posts is None:
      return render_template('nothing_found.html')
    return render_template('search.html', posts=posts)

@app.route('/api/create_post', methods=['POST'])
def create_post():
  if current_user.is_authenticated:
    data = request.form
    Posts.prisma().create(data={'authorId': current_user.id, 'content': data['content'], 'title': data['title']})
    return redirect('/dashboard')


@app.route('/api/change_name', methods=['POST'])
def change_name():
   if request.method == 'POST':
      if current_user.is_authenticated:
        data = request.form
        User.prisma().update(data={'name': data['name']}, where={'id': current_user.id})
        return redirect('/dashboard')

# Uncomment this to be able to create an account and signup. Then comment it again.
# @app.route('/signup')
# def signup():
#    User.prisma().create(data={'email': 'PUT EMAIL HERE TO HIT', 'password': hashlib.sha256('PUT YOUR PASSWORD HERE'.encode('utf-8')).hexdigest()})
#    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=3000)
