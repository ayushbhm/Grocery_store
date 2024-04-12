from flask import Blueprint, url_for,render_template,session ,request,redirect
import sqlite3



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/user_login')
def user_login():
    
    return render_template('auth/user_login.html')

@auth_bp.route('/admin_login')
def admin_login():
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/admin_login_check',methods=['GET', 'POST'])
def admin_login_check():
    
        if request.method == 'POST':
           username = request.form['username']
           password = request.form['password']

        
           con = sqlite3.connect('database.db')
           cursor = con.cursor()

        
           cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username,password))
           user = cursor.fetchone()
           con.close()
           

           if user:
            # Successful login
            
                return redirect(url_for('admin.admin_dashboard'))
           else:
           
              return "Invalid credentials"
           
    




@auth_bp.route('/user_login_check', methods=['GET', 'POST'])
def user_login_check():
    if request.method == 'POST':
        password =  request.form['password']
        username = request.form['username']
        

        con = sqlite3.connect('database.db')
        cursor = con.cursor()

        
        cursor.execute("  select * from users where username = ? AND password = ?", (username,password))
        user = cursor.fetchone()
        con.close()
        

        if user:
            session['username'] = user[0]
            return redirect(url_for('user_bp.user_home'))
        else:
            
            return "Wrong credentials"
    
    
        