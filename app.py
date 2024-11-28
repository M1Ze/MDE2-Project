from flask import Flask, render_template
from db_models import db, User, Patient, HealthData
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deps.db'

# connect SQLAlchemy to the app
db.init_app(app)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)