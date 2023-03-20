import os
from flask import Flask, Blueprint, render_template,url_for, redirect, request, flash, make_response, jsonify
from .models import Pokemon, UserPokemon, User, db
from flask_login import LoginManager, current_user, login_user, login_required, logout_user


login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized!')
    return redirect(url_for('login_page'))

def create_app():
  app = Flask(__name__, static_url_path='/static')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  db.init_app(app)
  login_manager.init_app(app)
  login_manager.login_view = "login_page"
  app.app_context().push()
  return app

app = create_app()

# Page Routes

#To update
@app.route("/", methods=['GET'])
def login():
   return redirect(url_for('home_page'))

@app.route("/app", methods=['GET'])
@app.route("/app/<int:pokemon_id>", methods=['GET'])
@login_required
# add @login_required decorator to require login
def home_page(pokemon_id=1):
  poke = Pokemon.query.filter_by(id = pokemon_id).all()
  pokemons = Pokemon.query.all()
  if pokemons is None:
    flash('Invalid id or unauthorized')
  else:
     return render_template("home.html", pokemons = pokemons,poke=poke)
    #pass relevant data to template

# Form Action Routes
@app.route('/', methods=['GET'])
@app.route('/signup', methods=['GET'])
def signup_page():
  return render_template('signup.html')

@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
def login_page():
  return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup_action():
  data = request.form  # get data from form submission
  newuser = User(username=data['username'], email=data['email'], password=data['password'])  # create user object
  try:
    db.session.add(newuser)
    db.session.commit()  # save user
    login_user(newuser)  # login the user
    flash('Account Created!')  # send message
    return redirect(url_for('home_page'))  # redirect to homepage
  except Exception:  # attempted to insert a duplicate user
    db.session.rollback()
    flash("username or email already exists")  # error message
  return redirect(url_for('login_page'))


@app.route('/login', methods=['POST'])
def login_action():
  data = request.form
  user = User.query.filter_by(username=data['username']).first()
  if user and user.check_password(data['password']):  # check credentials
    flash('Logged in successfully.')  # send message to next page
    login_user(user)  # login the user
    return redirect('/app')  # redirect to main page if login successful
  else:
    flash('Invalid username or password')  # send message to next page
  return redirect('/')

@app.route('/logout', methods=['GET'])
@login_required
def logout_action():
  logout_user()
  flash('Logged Out')
  return redirect(url_for('home_page'))

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)

