from flask import Blueprint, render_template, request, redirect, url_for, make_response, jsonify
from datetime import datetime, date
import calendar
from .models import Patient, CheckStatus
from . import db
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
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

    response = make_response(render_template('calendar.html',
                         calendar=cal,
                         month=month,
                         year=year,
                         month_name=month_name,
                         prescriptions=prescriptions,
                         today=today.date(),
                         day_of_month=today.day,
                         date=date,
                         user=current_user
                        ))
    # Add cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@views.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        frequency = int(request.form['frequency'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        
        patient = Patient(name=name, frequency=frequency, start_date=start_date)
        try:
            db.session.add(patient)
            db.session.commit()
            db.session.refresh(patient)
        except:
            db.session.rollback()
            raise
        
        return redirect(url_for('views.index'))
    return render_template('add_patient.html', user=current_user)

@views.route('/delete_patient', methods=['GET', 'POST'])
@login_required
def delete_patient():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        if patient_id:
            patient = Patient.query.get(patient_id)
            if patient:
                try:
                    db.session.delete(patient)
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise
        return redirect(url_for('views.index'))
    
    patients = Patient.query.all()
    return render_template('delete_patient.html', patients=patients, user=current_user)

@views.route('/update_status', methods=['POST'])
@login_required
def update_status():
    try:
        print(f"Received update_status request with form data: {request.form}") # Log form data
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
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating status: {str(e)}")  # This will show in Heroku logs
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/add_note', methods=['GET', 'POST'])
@login_required
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
    return render_template('add_note.html', patients=patients, user=current_user)

@views.route('/manage_notes')
@login_required
def manage_notes():
    # Only get patients that have notes
    patients = Patient.query.filter(Patient.notes.isnot(None)).all()
    return render_template('manage_notes.html', patients=patients, user=current_user)

@views.route('/edit_note/<int:patient_id>', methods=['POST'])
@login_required
def edit_note(patient_id):
    try:
        data = request.get_json()
        patient = Patient.query.get_or_404(patient_id)
        patient.notes = data.get('note', '')
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@views.route('/delete_note/<int:patient_id>', methods=['POST'])
@login_required
def delete_note(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        patient.notes = None
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@views.route('/edit_start_date/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_start_date(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            new_start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            new_frequency = int(request.form['frequency'])
            
            # Only delete check statuses if either start date or frequency changed
            if new_start_date != patient.start_date or new_frequency != patient.frequency:
                # Delete all existing check statuses for this patient
                CheckStatus.query.filter_by(patient_id=patient.id).delete()
                
                # Update the patient's start date and frequency
                patient.start_date = new_start_date
                patient.frequency = new_frequency
                db.session.commit()
            
            return redirect(url_for('views.index'))
        except Exception as e:
            db.session.rollback()
            # You might want to add proper error handling here
            return redirect(url_for('views.index'))
    
    return render_template('edit_start_date.html', patient=patient, user=current_user)