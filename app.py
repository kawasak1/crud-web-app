from flask import Flask, jsonify, render_template, request
from datetime import datetime
from classes import db, User, Patients, PatientDisease, Disease, Discover, DiseaseType, Specialize, Doctor, PublicServant, Country, Record 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/health_rep_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def homepage():
    return render_template('homepage.html')

# RENDERING PAGES
@app.route('/table/<table_name>')
def view_table(table_name):
    try:
        if table_name == 'users':
            data = User.query.order_by(User.email).all()
            columns = ['email', 'name', 'surname', 'salary', 'phone', 'cname']
            data = [row.to_dict() for row in data]
        elif table_name == 'patients':
            data = (
              db.session.query(
                  Patients.email, 
                  User.name, 
                  User.surname, 
                  Disease.disease_code, 
                  Disease.description
              )
              .join(User, Patients.email == User.email)
              .outerjoin(PatientDisease, Patients.email == PatientDisease.email)
              .outerjoin(Disease, PatientDisease.disease_code == Disease.disease_code)
              .order_by(Patients.email)
              .all()
            )
            columns = ['email', 'name', 'surname', 'disease_code', 'description']
            data = [dict(zip(columns, row)) for row in data]
        elif table_name == 'doctors':
            data = (
                db.session.query(
                    Doctor.email,
                    User.name,
                    User.surname,
                    Doctor.degree,
                    PublicServant.department,
                    db.func.count(Specialize.id).label("specialization_count")
                )
                .join(User, Doctor.email == User.email)
                .outerjoin(PublicServant, Doctor.email == PublicServant.email)
                .outerjoin(Specialize, Doctor.email == Specialize.email)
                .group_by(Doctor.email, User.name, User.surname, PublicServant.department, Doctor.degree)
                .order_by(Doctor.email)
                .all()
            )
            columns = ['email', 'name', 'surname', 'degree', "department", 'specialization_count']
            data = [dict(zip(columns, row)) for row in data]
        elif table_name == 'specializations':
            data = (
                db.session.query(
                    Doctor.email,
                    User.name,
                    User.surname,
                    DiseaseType.id.label("specialization_id"),
                    DiseaseType.description.label("specialization_description")
                )
                .join(User, Doctor.email == User.email)
                .join(Specialize, Doctor.email == Specialize.email)
                .join(DiseaseType, Specialize.id == DiseaseType.id)
                .order_by(Doctor.email)
                .all()
            )
            columns = ['email', 'name', 'surname', 'specialization_id', 'specialization_description']
            data = [dict(zip(columns, row)) for row in data]
        elif table_name == 'diseases':
            data = (
                db.session.query(
                    Disease.disease_code,
                    Disease.pathogen,
                    Disease.description.label("disease_description"),
                    Disease.id.label("disease_type_id"),
                    DiseaseType.description.label("disease_type_description"),
                    Discover.first_enc_date.label("first_encounter_date"),
                    Discover.cname.label("country_of_discover")
                )
                .outerjoin(DiseaseType, Disease.id == DiseaseType.id)
                .outerjoin(Discover, Disease.disease_code == Discover.disease_code)
                .order_by(Disease.disease_code)
                .all()
            )
            dataUpdated = []
            for row in data:
                lst = list(row)
                if lst[5]:
                  lst[5] = row[5].strftime("%Y-%m-%d")
                t = tuple(lst)
                dataUpdated.append(t)
            data = dataUpdated
            columns = ['disease_code', 'pathogen', 'disease_description', 'disease_type_id', 'disease_type_description', "first_encounter_date", "country_of_discover"]
            data = [dict(zip(columns, row)) for row in data]

        elif table_name == 'countries':
            data = (
                db.session.query(
                    Country.cname.label("country_name"),
                    Country.population,
                    db.func.count(User.email.distinct()).label("num_users"),
                    db.func.count(Patients.email.distinct()).label("num_patients"),
                    db.func.count(Doctor.email.distinct()).label("num_doctors"),
                    db.cast(db.func.avg(User.salary), db.Integer).label("avg_salary")
                )
                .outerjoin(User, User.cname == Country.cname)
                .outerjoin(Patients, Patients.email == User.email)
                .outerjoin(Doctor, Doctor.email == User.email)
                .group_by(Country.cname, Country.population)
                .order_by(Country.cname)
                .all()
            )
            columns = ['country_name', 'population', 'num_users', 'num_patients', 'num_doctors', 'avg_salary']
            data = [dict(zip(columns, row)) for row in data]
        
        elif table_name == 'records':
            data = (
                db.session.query(
                    Record.email,
                    Record.cname,
                    Record.disease_code,
                    Disease.description,
                    Record.total_deaths,
                    Record.total_patients,
                )
                .outerjoin(Disease, Disease.disease_code == Record.disease_code)
                .order_by(Record.email).all()
            )
            columns = ['email', 'cname', 'disease_code', 'Disease_Description', 'total_deaths', 'total_patients']
            data = [dict(zip(columns, row)) for row in data]

        else:
            return jsonify({'error': 'Invalid table name'}), 404

        return render_template('table.html', table_name=table_name, columns=columns, data=data, getattr=getattr)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# UPDATING TABLE ENTRY
@app.route('/update/<table_name>', methods=['POST'])
def update_table(table_name):
    try:
        data = request.get_json()

        # FOR USERS TABLE
        if table_name == 'users':
            user_email = data.get('old', {}).get('email')
            user = User.query.filter_by(email=user_email).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            user.email = data.get('email', user.email) or None
            user.name = data.get('name', user.name) or None
            user.surname = data.get('surname', user.surname) or None
            user.salary = data.get('salary', user.salary) or None
            user.phone = data.get('phone', user.phone) or None
            user.cname = data.get('cname', user.cname) or None

            db.session.commit()

        # FOR PATIENTS TABLE
        elif table_name == 'patients':
            patient_email = data.get('old', {}).get('email')
            patient = Patients.query.filter_by(email=patient_email).first()
            patient_disease = PatientDisease.query.filter_by(email=patient_email).first()
            user = User.query.filter_by(email=patient_email).first()

            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            disease_code = data.get('disease_code')
            if disease_code:
              disease = Disease.query.filter_by(disease_code=disease_code,).first()
              if not disease:
                  return jsonify({'error': 'Disease not found'}), 404

              if not patient_disease:
                  new_patient_disease = PatientDisease(
                      email=data.get('email', user.email) or None,
                      disease_code=disease_code,
                  )
                  db.session.add(new_patient_disease)
              else:
                  patient_disease.disease_code = disease_code or None

            user.email = data.get('email', user.email) or None
            user.name = data.get('name', user.name) or None
            user.surname = data.get('surname', user.surname) or None

            db.session.commit()

        #FOR DOCTORS TABLE
        elif table_name == 'doctors':
            doctor_email = data.get('old', {}).get('email')
            doctor = Doctor.query.filter_by(email=doctor_email).first()
            user = User.query.filter_by(email=doctor_email).first()

            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404

            doctor.degree = data.get('degree', doctor.degree) or None

            user.email = data.get('email', user.email) or None
            user.name = data.get('name', user.name) or None
            user.surname = data.get('surname', user.surname) or None

            publicservant = PublicServant.query.filter_by(email=doctor_email).first()
            department = data.get('department')
            if not publicservant and department:
                new_public_servant = PublicServant(
                    email=data.get('email', user.email),
                    department=department,
                )
                db.session.add(new_public_servant)
            else:
                publicservant.email = data.get('email', user.email) or None
                publicservant.department = department or None

            db.session.commit()

        # FOR SPECIALIZATIONS TABLE
        elif table_name == 'specializations':
            doctor_email = data.get('old', {}).get('email')
            specialize_id = data.get('old', {}).get('specialization_id')
            specialization = Specialize.query.filter_by(email=doctor_email, id=specialize_id).first()

            if not specialization:
                return jsonify({'error': 'Specialization not found'}), 404
            
            id = data.get('specialization_id')
            diseasetype = DiseaseType.query.filter_by(id=id).first()

            if not diseasetype:
                return jsonify({'error': 'Disease ID not found'}), 404

            specialization.id = id or None

            db.session.commit()

        # FOR DISEASES TABLE
        elif table_name == 'diseases':
            disease_code = data.get('old', {}).get('disease_code')
            disease = Disease.query.filter_by(disease_code=disease_code,).first()
            discover = Discover.query.filter_by(disease_code=disease_code,).first()

            if not disease:
                return jsonify({'error': 'Disase not found'}), 404

            disease.pathogen = data.get('pathogen', disease.pathogen) or None
            disease.description = data.get('disease_description', disease.description) or None
            disease.id = data.get('disease_type_id', disease.id) or None

            if discover:
                discover_date = datetime.strptime(data.get('first_encounter_date'), '%Y-%m-%d').date() if data.get('first_encounter_date') else None
                discover.first_enc_date = discover_date or None
                discover.cname = data.get('country_of_discover', discover.cname) or None
            else:
                discover_date = datetime.strptime(data.get('first_encounter_date'), '%Y-%m-%d').date() if data.get('first_encounter_date') else None
                new_discover = Discover(
                    disease_code=disease_code,
                    first_enc_date=discover_date,
                    cname=data.get('country_of_discover'),
                )

                if data.get('country_of_discover'): db.session.add(new_discover)

            db.session.commit()

        # FOR COUNTRIES TABLE
        elif table_name == 'countries':
            cname = data.get('old', {}).get('country_name')
            country = Country.query.filter_by(cname=cname).first()

            if not country:
                return jsonify({'error': 'Country not found'}), 404

            country.cname = data.get('country_name', country.cname) or None
            country.population = data.get('population', country.population) or None

            db.session.commit()

        # FOR RECORDS TABLE
        elif table_name == 'records':
            email = data.get('old', {}).get('email')
            cname = data.get('old', {}).get('cname')
            disease_code = data.get('old', {}).get('disease_code')
            record = Record.query.filter_by(email=email, cname=cname, disease_code=disease_code).first()

            if not record:
                return jsonify({'error': 'Record not found'}), 404

            record.email = data.get('email', record.email) or None
            record.cname = data.get('cname', record.cname) or None
            record.disease_code = data.get('disease_code', record.disease_code) or None
            record.total_deaths = data.get('total_deaths', record.total_deaths) or None
            record.total_patients = data.get('total_patients', record.total_patients) or None

            db.session.commit()

        else:
            return jsonify({'error': 'Invalid table name'}), 400

        return jsonify({'message': 'Data updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#ADDING ENTRY TO TABLE
@app.route('/add/<table_name>', methods=['POST'])
def add_to_table(table_name):
    try:
        data = request.get_json()

        # FOR USERS TABLE
        if table_name == 'users':
            user_email = data.get('email')
            if User.query.filter_by(email=user_email).first():
                return jsonify({'error': 'User already exists'}), 400

            new_user = User(
                name=data.get('name') or None,
                email=user_email or None,
                surname=data.get('surname') or None,
                salary=data.get('salary') or None,
                phone=data.get('phone') or None,
                cname=data.get('cname') or None
            )

            db.session.add(new_user)
            db.session.commit()

        # FOR PATIENTS TABLE
        elif table_name == 'patients':
            patient_email = data.get('email')
            if not patient_email:
                return jsonify({'error': 'Email cannot be empty'}), 400
            if Patients.query.filter_by(email=patient_email).first():
                return jsonify({'error': 'Patient already exists'}), 400
            
            user_email = data.get('email')
            if not User.query.filter_by(email=user_email).first():
                new_user = User(
                    email=user_email,
                )
                db.session.add(new_user)
                db.session.commit()

            new_patient = Patients(
                email=patient_email,
            )
            disease_code = data.get('disease_code')
            disease = Disease.query.filter_by(disease_code=disease_code,).first()
            if not disease:
                return jsonify({'error': 'Disease not found'}), 404
            new_patient_disease = PatientDisease(
                email=patient_email,
                disease_code=disease_code
            )

            db.session.add(new_patient)
            db.session.commit()
            if disease_code: db.session.add(new_patient_disease)
            db.session.commit()

        #FOR DOCTORS TABLE
        elif table_name == 'doctors':
            doctor_email = data.get('email')
            if Doctor.query.filter_by(email=doctor_email).first():
                return jsonify({'error': 'Doctor already exists'}), 400
            
            user_email = data.get('email')
            if not User.query.filter_by(email=user_email).first():
                new_user = User(
                email=user_email,
                )
                db.session.add(new_user)
                db.session.commit()

            new_doctor = Doctor(
                email=doctor_email,
                degree=data.get('degree') or None
            )

            new_public_servant = PublicServant(
                email=doctor_email,
                department=data.get('department') or None
            )
            db.session.add(new_public_servant)

            db.session.add(new_doctor)
            db.session.commit()

        # FOR SPECIALIZATIONS TABLE
        elif table_name == 'specializations':
            doctor_email = data.get('email')
            doctor = Doctor.query.filter_by(email=doctor_email).first()

            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            id = data.get('specialization_id')
            diseasetype = DiseaseType.query.filter_by(id=id).first()

            if not diseasetype:
                return jsonify({'error': 'Disease ID not found'}), 404
            
            specialize_id = data.get('specialization_id')
            if Specialize.query.filter_by(email=doctor_email, id=specialize_id).first():
                return jsonify({'error': 'Specialization already exists'}), 400

            new_specialize = Specialize(
                email=doctor_email,
                id=data.get('specialization_id') or None
            )

            db.session.add(new_specialize)
            db.session.commit()

        # FOR DISEASES TABLE
        elif table_name == 'diseases':
            disease_code = data.get('disease_code')
            if Disease.query.filter_by(disease_code=disease_code,).first():
                return jsonify({'error': 'Disease already exists'}), 400
            
            new_disease = Disease(
                disease_code=disease_code,
                pathogen=data.get('pathogen') or None,
                description=data.get('disease_description') or None,
                id=data.get('disease_type_id') or None,
            )

            discover_date = datetime.strptime(data.get('first_encounter_date'), '%Y-%m-%d').date() if data.get('first_encounter_date') else None

            new_discover = Discover(
                disease_code=disease_code,
                first_enc_date=discover_date,
                cname=data.get('country_of_discover'),
            )

            db.session.add(new_disease)
            db.session.commit()
            if data.get('country_of_discover'): db.session.add(new_discover)
            db.session.commit()

        # FOR COUNTRIES TABLE
        elif table_name == 'countries':
            cname = data.get('country_name')
            if Country.query.filter_by(cname=cname).first():
                return jsonify({'error': 'Country already exists'}), 400

            new_country = Country(
                cname=cname,
                population=data.get('population')
            )

            db.session.add(new_country)
            db.session.commit()

        # FOR RECORDS TABLE
        elif table_name == 'records':
            email = data.get('email')
            cname = data.get('cname')
            disease_code = data.get('disease_code')
            if Record.query.filter_by(email=email, cname=cname, disease_code=disease_code).first():
                return jsonify({'error': 'Record already exists'}), 400

            doctor = Doctor.query.filter_by(email=email).first()
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            country = Country.query.filter_by(cname=cname).first()
            if not country:
                return jsonify({'error': 'Country not found'}), 404
            disease = Disease.query.filter_by(disease_code=disease_code,).first()
            if not disease:
                return jsonify({'error': 'Disase not found'}), 404
            
            new_record = Record(
                email=email,
                cname=cname,
                disease_code=disease_code,
                total_deaths=data.get('total_deaths') or None,
                total_patients=data.get('total_patients') or None,
            )

            db.session.add(new_record)
            db.session.commit()

        else:
            return jsonify({'error': 'Invalid table name'}), 400

        return jsonify({'message': 'Data added successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# DELETING TABLE ENTRY
@app.route('/delete/<table_name>', methods=['POST'])
def delete_from_table(table_name):
    try:
        data = request.get_json()

        # FOR USERS TABLE
        if table_name == 'users':
            user_email = data.get('email')
            user = User.query.filter_by(email=user_email).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            db.session.delete(user)
            db.session.commit()

        # FOR PATIENTS TABLE
        elif table_name == 'patients':
            patient_email = data.get('email')
            patient = Patients.query.filter_by(email=patient_email).first()

            if not patient:
                return jsonify({'error': 'Patient not found'}), 404

            db.session.delete(patient)
            db.session.commit()

        #FOR DOCTORS TABLE
        elif table_name == 'doctors':
            doctor_email = data.get('email')
            doctor = Doctor.query.filter_by(email=doctor_email).first()

            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404

            db.session.delete(doctor)
            db.session.commit()

        # FOR SPECIALIZATIONS TABLE
        elif table_name == 'specializations':
            doctor_email = data.get('email')
            specialize_id = data.get('specialization_id')
            specialization = Specialize.query.filter_by(email=doctor_email, id=specialize_id).first()

            if not specialization:
                return jsonify({'error': 'Specialization not found'}), 404

            db.session.delete(specialization)
            db.session.commit()

        # FOR DISEASES TABLE
        elif table_name == 'diseases':
            disease_code = data.get('disease_code')
            disease =  Disease.query.filter_by(disease_code=disease_code,).first()

            if not disease:
                return jsonify({'error': 'Disease not found'}), 404

            db.session.delete(disease)
            db.session.commit()

        # FOR COUNTRIES TABLE
        elif table_name == 'countries':
            cname = data.get('country_name')
            country =  Country.query.filter_by(cname=cname).first()

            if not country:
                return jsonify({'error': 'Country not found'}), 404

            db.session.delete(country)
            db.session.commit()

        # FOR RECORDS TABLE
        elif table_name == 'records':
            email = data.get('email')
            cname = data.get('cname')
            disease_code = data.get('disease_code')
            record = Record.query.filter_by(email=email, cname=cname, disease_code=disease_code).first()

            if not record:
                return jsonify({'error': 'Record not found'}), 404

            db.session.delete(record)
            db.session.commit()

        else:
            return jsonify({'error': 'Invalid table name'}), 400

        return jsonify({'message': 'Data deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
