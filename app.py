from flask import Flask,render_template,request,url_for,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import Length, EqualTo, DataRequired, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_user,UserMixin
import functools




import os
SECRET_KEY = os.urandom(32)



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

#csrf = CSRFProtect(app)
class LoginForm(FlaskForm):
    email = StringField(label='Email :', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    submit = SubmitField(label='Log in')

class RegistrationForm(FlaskForm):
    first_name = StringField(label='First Name:',validators=[DataRequired()])
    last_name = StringField(label='Last Name:',validators=[DataRequired()])
    email = StringField(label='Email :', validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(80),nullable=False)
    last_name=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(50),nullable=False,unique=True)
    password=db.Column(db.String(80),nullable=False)
    def __init__(self,first_name,last_name,email,password):
        self.first_name=first_name
        self.last_name=last_name
        self.email=email
        self.password=password
    def validate(self,attempted_password):
        if hash(self.password)==hash(attempted_password):
            return True
        return False






@app.route('/signup',methods=['GET','POST'])
def start():
    form=RegistrationForm(request.form)
    message=''
    print(form.validate_on_submit(),request.method=="POST")
    if form.validate_on_submit() or request.method=="POST":
        name1=form.first_name.data
        name2=form.last_name.data
        email=form.email.data
        password=form.password.data


        print(f"{name1} , {name2}, {email},{password}")
        user=User(name1,name2,email,password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
        # render_template("test_template_2.html")


    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')
            #message+=err_msg +' '
    return render_template("register.html",form=form)



@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first() #gets the user
        if user and user.validate(form.password.data):
            session['email'] = user.email
            session['name']=user.first_name + " " + user.last_name
            login_user(user)
            flash(f"You are logged in as {user.first_name} {user.last_name}")

            print(f"{session['email']}")
            return redirect(url_for("page"))
        else:
            flash(f"Incorrect password and/or email")



    return render_template("login_page.html",form=form)
def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "email" not in session:
            return redirect(url_for("login"))
        return func()

    return secure_function

@app.route('/page',methods=['POST','GET'])
@login_required
def page():
    if request.method=="POST":
        session.clear()
        return redirect(url_for("login"))



    return render_template("page.html",first_name=session.get("name"))

if __name__ == '__main__':
    app.run(debug=True)

    #db.create_all()