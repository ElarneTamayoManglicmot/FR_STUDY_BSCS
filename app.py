from flask import Flask, render_template
from face_recognition_functions import face_recog_bp
from crud import crud

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(face_recog_bp)
app.register_blueprint(crud)

@app.route('/')
def index():
    return render_template('hypoFARFRR/frrfar.html')

if __name__ == '__main__':
    app.run(debug=True)
