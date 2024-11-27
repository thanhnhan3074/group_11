import flask
import bcrypt
import re
from flask_mysqldb import MySQL
import mysql.connector
from flask import render_template, redirect, url_for,request, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = flask.Flask(__name__)

'''Project configuration - Cau hinh cho du an'''

#Secret key - khoa dac biet
app.config.from_object("config")
app.config.get("SECRET_KEY")
app.config.get("FLASK_ENV")

#Database setup - cau hinh database tu config.py
#Hien tai chua dung toi
app.config.get("MYSQL_HOST")
app.config.get("MYSQL_USER")
app.config.get("MYSQL_PASSWORD")
app.config.get("MYSQL_DB")
cursor_sql = MySQL(app=app)



'''Khoi tao nguoi dung theo dang ID, Username'''
class User(UserMixin):
    def __init__(self,id,username,role):
        self.id = id
        self.username = username
        self.role = role

'''kiem tra thong tin nguoi dung 
trong qua trinh tai neu nguoi dung do 
khop thong tin tren thì tra ve ket qua'''

loginapp = LoginManager(app=app)
loginapp.init_app(app)
# loginapp.login_view(redirect(url_for('return_signin')))
''' ! - Chua chinh duoc trang mac dinh la dang nhap'''

'''ketnoi CSDL'''
db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'thanhnhan3072004',  
    database = 'usermanagement'
)
cursor = db.cursor(dictionary=True)


'''Tai ttin nguoi dung tu 
CSDL len he thong'''
@loginapp.user_loader
def loading_user(user_id):
    try:
        query_user = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query_user,(user_id,))
        account = cursor.fetchone()
        if account:
            return User(id=account['id'],username=account['username'],role=account['role'])
        else:
            return None
    except mysql.connector.errors.InternalError:
        
        return None
    

@app.route("/signin", methods =["GET","POST"])
def return_signin():
    if request.method == "POST":
        message = ""
        username = request.form['Username']
        password = request.form['Password']
        
        query_user = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query_user,[username,password])
        account = cursor.fetchone()

        
        if account:
            login_user(User(id=account["id"],username=account["username"],role=account['role']))
            #tao phien nguoi dung
            session[f'{username} has logged in'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = account['role']
            return render_template("home.html")
            

        #xoa phien dang nhap cũ neu nguoi dung dang nhap o mot phien khac
        if session.get(f'{username} has logged in '):
            del session[f'{username} has logged in']
        #Neu thong tin dang nhap ko dung
        else:
            # return f"{username} does not exists"
            message = f"User name or password are not correct"
            return redirect(url_for('return_signin',msg = message))

    return render_template("signin.html")


@app.route("/signup", methods=["GET","POST"])
def return_signup():

    notification = ""
    #Neu cac truong thong tin duoc dien day du, se tien hanh cac hinh thuc doi chieu o ben duoi 
    if request.method == "POST" and 'new Username' in request.form and 'new Password' in request.form and 'email' in request.form:
        username = request.form['new Username']
        password = request.form['new Password']
        email = request.form['email']
        role = "assign only"
        #Truy van cac truong can so sanh gom username,pass,role,email
        query_user = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s AND email = %s"
        cursor.execute(query_user,(username,password,role,email))
        new_account = cursor.fetchone()
        #Neu cac o thong tin day du se tien hanh doi chieu thong tin (records) trong CSDL de kiem tra thong tin có ton tai hay khong



        if new_account:
            notification = "Account already exist"
        #kiem tra chuoi email bang phuong thung so sanh re.match voi params email

        


        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            notification = "Invalid email address"
        #kime tra cac ki tu can co trong email
        elif not re.match(r'[A-Za-z0-9]+',username):
            notification = "Username must contain only characters and numbers !"
        #neu cac o thong tin bi trong thi se co thong bao
        elif not username or not password or not email:
            notification = "You must fill out the form before signing in"
        
        else:
            #Sau khi kiem tra cac dieu kien tren thì tien hanh tao tk moi
            # salt = bcrypt.gensalt(rounds=15)
            # encrypt_pwd = bcrypt.hashpw(password=password.encode('utf-8'),salt=bytes(salt))
            sign_up_exc = '''INSERT INTO users (username,password,role,email) VALUES (%s,%s,%s,%s)'''
            cursor.execute(sign_up_exc,(username,password,role,email))
            notification = "Sign up succcessfully !!!"
            db.commit()
    #Neu cac o dien thong tin chua co gi thi tra ve POST 
    elif request.method == "POST":
        notification = "You must fill out the form before signing in"
    return render_template("signup.html",msg = notification)






@app.route("/home", methods=["GET","POST"])
# @login_required
def return_homepage():
    return render_template("home.html")



@app.route("/dashboard")
# @login_required
def dashboard():
    
    try:
        if session.get("role") != "admin":
            return render_template("home.html",msg="You are not allowed to access this")
        else:
            users_query = "SELECT * FROM users"
            cursor.execute(users_query)
            users = cursor.fetchall()
            return render_template('dashboard.html',users=users)
    except mysql.connector.errors.InternalError:
        return render_template("dashboard.html")


@app.route("/edit",methods=["GET","POST"])
# @login_required
def edit():
    notification = "" 
    users = [] 
    

    try:
        if session.get("role") != "admin":
            return render_template("home.html",msg="You are not allowed to access this")
        if request.method == "POST":
            try:
                search = request.form.get("search")
                id = request.form.get("id")
                username = request.form.get("username")
                email = request.form.get("email")
                role = request.form.get("role")
                check_user = "SELECT * FROM users WHERE username = %s "
                cursor.execute(check_user,[search])
                users = cursor.fetchall()
                if users is None:
                    notification = f"user {search} not found"
                    
                else:
                    notification = f"user {search} found"
                    # id = request.form["id"]
                    # username = request.form["username"]
                    # email = request.form["email"]
                    # role = request.form["role"]
                    
                    update_user = '''
                        UPDATE users 
                        SET username = %s, email = %s, role =%s
                        WHERE id = %s
                    '''
                    cursor.execute(update_user,(username,email,role,id))
                    flash("complete")
                    
                    db.commit()
                    return render_template("edit.html",users=users ,msg = notification)
            except TypeError:
                return render_template("edit.html",users=users ,msg = notification)
    except mysql.connector.errors.InternalError as error:
        session.accessed = True
        notification = f"user {search}: {error}"
        return None
    except TypeError:
        return render_template("edit.html" ,msg = notification)
    
        
    return render_template("edit.html" ,msg = notification)
        
            


'''Dang xuat voi dieu kien phien dang nhap cua 
Nguoi dung ton tai'''
@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for('return_signin'))

if __name__ == '__main__':
    app.run()



'''Redirect: 
Co nghia la chuyen 
truc tiep ve trang da dinh san'''

'''
POST:
Lay thong tin du lieu tu
nguoi dung cuo
'''

'''
GET
tra ve ket qua cho 
nguoi dung cuoi
'''