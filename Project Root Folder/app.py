from flask import Flask,render_template
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp


''''REgistering all blueprints that we want to use'''
app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

'''This is the upload folder where all images will be uploaded'''
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('home.html')


app.secret_key = 'secret_key_for_grocery-_tore'

app.debug = True
if __name__ == '__main__': 
 app.run()


