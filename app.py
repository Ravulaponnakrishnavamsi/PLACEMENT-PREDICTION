from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle
import numpy as np

# Initialize Flask
app = Flask(__name__)

# Configure database (creates placement.db automatically)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define table schema
class PlacementRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer)
    iq = db.Column(db.Float)
    prev_sem = db.Column(db.Float)
    cgpa = db.Column(db.Float)
    academic = db.Column(db.Float)
    internship = db.Column(db.Integer)
    extra_curr = db.Column(db.Float)
    comm = db.Column(db.Float)
    projects = db.Column(db.Float)
    result = db.Column(db.String(20))

# Create the database
with app.app_context():
    db.create_all()

# Load trained model
with open('placement_model.pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        college_id = float(request.form['College_ID'])
        iq = float(request.form['IQ'])
        prev_sem = float(request.form['Prev_Sem_Result'])
        cgpa = float(request.form['CGPA'])
        academic = float(request.form['Academic_Performance'])
        internship = float(request.form['Internship_Experience'])
        extra_curr = float(request.form['Extra_Curricular_Score'])
        comm = float(request.form['Communication_Skills'])
        projects = float(request.form['Projects_Completed'])

        features = np.array([[iq, prev_sem, cgpa, academic, internship,
                              extra_curr, comm, projects, college_id]])
        prediction = model.predict(features)
        output = 'Placed' if prediction[0] == 1 else 'Not Placed'

        # Save record to database
        record = PlacementRecord(
            college_id=college_id,
            iq=iq,
            prev_sem=prev_sem,
            cgpa=cgpa,
            academic=academic,
            internship=internship,
            extra_curr=extra_curr,
            comm=comm,
            projects=projects,
            result=output
        )
        db.session.add(record)
        db.session.commit()

        return render_template('index.html', prediction_text=f"🎯 Student is {output}")
@app.route('/records')
def records():
    all_data = PlacementRecord.query.all()
    return render_template('records.html', records=all_data)

def chatbot_ui():
    return render_template('chatbot.html')

@app.route('/chat_predict', methods=['POST'])
def chat_predict():
    data = request.get_json()
    answers = list(map(float, data['answers']))

    features = np.array([answers])  # single input
    prediction = model.predict(features)[0]

    result = "🎉 Great! This student is likely to be *PLACED!*" if prediction == 1 else "😞 Unfortunately, this student is *NOT placed.*"
    return jsonify({'prediction': result})


if __name__ == "__main__":
    app.run(debug=True)
