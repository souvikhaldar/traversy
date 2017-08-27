from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
app = Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='245492'
app.config['MYSQL_DB']='hisabkitab'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql=MySQL(app)



@app.route('/')
def index():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")
class RegisterForm(Form):
	name=StringField('Name',[validators.Length(min=1,max=30)])
	username=StringField('Username',[validators.Length(min=5,max=100)])
	email=StringField('Email',[validators.Length(min=5,max=50)])
	password=PasswordField('Password',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
		])
	confirm=PasswordField('Confirm Password')
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))
        cur=mysql.connection.cursor()
        cur.execute("insert into users(name,email,username,password) values (%s, %s, %s, %s)",(name,email,username,password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered','success')
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username= request.form['username']
        password_candidate=request.form['password']
        cur=mysql.connection.cursor()
        #get user by username
        result=cur.execute("select * from users where username=%s",[username])
        if result>0:
            data=cur.fetchone()
            password=data['password']
            #compare the passwords
            if sha256_crypt.verify(password_candidate,password):
                app.logger.info('Password matched')
            else:
                app.logger.info('Password not matched')
        else:
            app.logger.info('No user')

    return render_template('login.html')
if __name__=='__main__':
    app.secret_key='12345'
    app.run(debug=True)
