from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(30))
    surname = db.Column(db.String(40))
    salary = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    cname = db.Column(db.String(50))

    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'surname': self.surname,
            'salary': self.salary,
            'phone': self.phone,
            'cname': self.cname
        }

class Patients(db.Model):
    __tablename__ = 'patients'
    email = db.Column(db.String(60), primary_key=True)

    def to_dict(self):
        return {
            'email': self.email,
        }

class PatientDisease(db.Model):
    __tablename__ = 'patientdisease'
    email = db.Column(db.String(60), primary_key=True)
    disease_code = db.Column(db.String(50))

    def to_dict(self):
        return {
            'email': self.email,
            "disease_code": self.disease_code,
        }

class Disease(db.Model):
    __tablename__ = 'disease'
    disease_code = db.Column(db.String(50), primary_key=True)
    pathogen = db.Column(db.String(20))
    description = db.Column(db.String(140))
    id = db.Column(db.Integer)

    def to_dict(self):
        return {
            "disease_code": self.disease_code,
            "pathogen": self.pathogen,
            "description": self.description,
            "id": self.id,
        }

class Discover(db.Model):
    __tablename__ = 'discover'
    disease_code = db.Column(db.String(50), primary_key=True)
    cname = db.Column(db.String(50), primary_key=True)
    first_enc_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "disease_code": self.disease_code,
            "cname": self.cname,
            "first_enc_date": self.first_enc_date,
        }

class DiseaseType(db.Model):
    __tablename__ = 'diseasetype'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140))

    def to_dict(self):
        return {
            'id': self.id,
            "description": self.disease_code,
        }

class Specialize(db.Model):
    __tablename__ = 'specialize'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), primary_key=True)

    def to_dict(self):
        return {
            'id': self.email,
            'email': self.email,
        }

class Doctor(db.Model):
    __tablename__ = 'doctor'
    email = db.Column(db.String(60), primary_key=True)
    degree = db.Column(db.String(20))

    def to_dict(self):
        return {
            'email': self.email,
            'degree': self.degree,
        }
    

class PublicServant(db.Model):
    __tablename__ = 'publicservant'
    email = db.Column(db.String(60), primary_key=True)
    department = db.Column(db.String(50))

    def to_dict(self):
        return {
            'email': self.email,
            'department': self.department,
        }

class Country(db.Model):
    __tablename__ = 'country'
    cname = db.Column(db.String(50), primary_key=True)
    population = db.Column(db.BigInteger)

    def to_dict(self):
        return {
            'cname': self.cname,
            'population': self.population,
        }

class Record(db.Model):
    __tablename__ = 'record'
    email = db.Column(db.String(60), primary_key=True)
    cname = db.Column(db.String(50), primary_key=True)
    disease_code = db.Column(db.String(50), primary_key=True)
    total_deaths = db.Column(db.Integer)
    total_patients = db.Column(db.Integer)
    def to_dict(self):
        return {
            'email': self.email,
            'cname': self.cname,
            "disease_code": self.disease_code,
            'total_deaths': self.total_deaths,
            'total_patients': self.total_patients,
        }