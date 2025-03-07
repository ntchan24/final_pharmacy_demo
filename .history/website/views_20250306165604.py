from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, date
import calendar
from .models import Patient, CheckStatus
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def index():
    today = datetime.now()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    patients = Patient.query.all()
    prescriptions = {}
    
    for week in cal:
        for day in week:
            if day != 0:
                current_date = date(year, month, day)
                prescriptions[current_date] = []

                for patient in patients:
                    start_date = patient.start_date.date()
                    
                    # Calculate if patient needs prescription on this date
                    if current_date >= start_date and (current_date - start_date).days % (patient.frequency * 7) == 0:
                        # This is a prescription date
                        check_status = CheckStatus.query.filter_by(
                            patient_id=patient.id,
                            date=current_date
                        ).first()
                        
                        # Always add the prescription, regardless of checked boxes or not 
                        prescriptions[current_date].append({
                            'patient': patient,
                            'status': check_status or None
                        })

    return render_template('calendar.html',
                         calendar=cal,
                         month=month,
                         year=year,
                         month_name=month_name,
                         prescriptions=prescriptions,
                         today=today.date(),
                         day_of_month=today.day,
                         date=date,
                        )

@views.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        frequency = int(request.form['frequency'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        
        patient = Patient(name=name, frequency=frequency, start_date=start_date)
        db.session.add(patient)
        db.session.commit()
        
        return redirect(url_for('views.index'))
    return render_template('add_patient.html')

@views.route('/delete_patient', methods=['GET', 'POST'])
def delete_patient():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        if patient_id:
            patient = Patient.query.get(patient_id)
            if patient:
                db.session.delete(patient)
                db.session.commit()
        return redirect(url_for('views.index'))
    
    patients = Patient.query.all()
    return render_template('delete_patient.html', patients=patients)

@views.route('/update_status', methods=['POST'])
def update_status():
    patient_id = request.form['patient_id']
    date_str = request.form['date']
    status_type = request.form['status_type']
    checked = request.form['checked'] == 'true'
    
    current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    status = CheckStatus.query.filter_by(patient_id=patient_id, date=current_date).first()
    
    if not status:
        status = CheckStatus(patient_id=patient_id, date=current_date)
        db.session.add(status)
    
    setattr(status, status_type, checked)
    db.session.commit()
    
    return 'OK'

@views.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        note = request.form['note']
        patient = Patient.query.get(patient_id)
        if patient:
            patient.notes = note
            db.session.commit()
            return redirect(url_for('views.index'))
    patients = Patient.query.all()
    return render_template('add_note.html', patients=patients)