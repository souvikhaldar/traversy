from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
#from data import Articles
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)
#Articles=Articles()

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

#articles
@app.route('/articles')
def articles():
    #return render_template('articles.html',articles=Articles)

    
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles")
    articles=cur.fetchall()
    if result>0:
        return render_template('articles.html',articles=articles)
    else:
        msg="No articles found"
        return render_template('articles.html',msg=msg)
    #close connection
    cur.close()

@app.route('/articles/<string:id>/')
def article(id):
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles where id= %s",[id])
    
    article=cur.fetchone()
    return render_template('article.html',article=article)
    
    
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
                session['logged_in']=True
                session['username']=username
                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error='Password wrong'
                return render_template('login.html',error=error)
            #close connection
            cur.close()
        else:
            error='Username not found'
            return render_template('login.html',error=error)
            
    return render_template('login.html')
#check if logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, please log in','danger')
            return redirect(url_for('login'))
    return wrap



#log out
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out",'success')
    return redirect(url_for('login'))
#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("select * from articles")
    articles=cur.fetchall()
    if result>0:
        return render_template('dashboard.html',articles=articles)
    else:
        msg="No articles found"
        return render_template('dashboard.html',msg=msg)
    #close connection
    cur.close()
#article form
class ArticleForm(Form):
	title=StringField('Title',[validators.Length(min=1,max=300)])
	body=TextAreaField('Body',[validators.Length(min=10)])

#add article
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        title=form.title.data
        body=form.body.data

        #create cursor
        cur=mysql.connection.cursor()
        cur.execute("insert into articles(title,body,author) values(%s,%s,%s)",(title,body,session['username']))
        #commit
        mysql.connection.commit()
        #close connection
        cur.close()
        flash('Article created','success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form)
#edit article        
@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    cur=mysql.connection.cursor()
    #get article by id
    result=cur.execute("select * from articles where id=%s",[id])
    article=cur.fetchone()
    #get form
    form=ArticleForm(request.form)
    #populate article form fields
    form.title.data=article['title']
    form.body.data=article['body']

    
    if request.method=='POST' and form.validate():
        title=request.form['title']
        body=request.form['body']

        #create cursor
        cur=mysql.connection.cursor()
        cur.execute("update articles set title=%s,body=%s where id=%s",(title,body,id))
        #commit
        mysql.connection.commit()
        #close connection
        cur.close()
        flash('Article updated','success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html',form=form)

#delete article
@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
           cur=mysql.connection.cursor()
           cur.execute("delete from articles where id=%s",[id])
           mysql.connection.commit()
           cur.close()
           
           flash('Article deleted','success')
           return redirect(url_for('dashboard'))
           
if __name__=='__main__':
    app.secret_key='12345'
    app.run(debug=True)
