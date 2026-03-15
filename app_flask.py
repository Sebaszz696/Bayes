from flask import Flask
from routes import bp as main_bp

app = Flask(__name__, static_folder='static', template_folder='templates')
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
