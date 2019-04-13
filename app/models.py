from app import db

class Employee_login(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))


class Patient_login(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    p_id = db.Column(db.String(255), unique=True)
    p_password = db.Column(db.String(255))

class Patient_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), nullable=True, unique=True)
    phone = db.Column(db.String(20), nullable=True, unique=False)
    added = db.Column(db.String(20), nullable=False, unique=False, default='No')
    h_disease=db.relationship('Heart_data',backref='pname') 
    d_disease=db.relationship('Disease_Present_Data',backref='dname') #for one to one relationship only add uselist=false

class Heart_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    cp = db.Column(db.Float)
    trestbps = db.Column(db.Float)
    chol = db.Column(db.Float)
    fbs= db.Column(db.Float)
    restecg = db.Column(db.Float)
    thalach = db.Column(db.Float)
    exang = db.Column(db.Float)
    oldpeak = db.Column(db.Float)
    slope = db.Column(db.Float)
    ca = db.Column(db.Float)
    thal = db.Column(db.Float)
    pid=db.Column(db.Integer, db.ForeignKey('patient_data.id'))


class Disease_Present_Data(db.Model):
    did=db.Column(db.Integer, primary_key=True)
    disease=db.Column(db.Integer)
    pid=db.Column(db.Integer, db.ForeignKey('patient_data.id'))
