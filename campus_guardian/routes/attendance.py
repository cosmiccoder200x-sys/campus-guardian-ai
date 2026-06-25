from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.subject import Subject
from models.attendance import AttendanceRecord
from app import db
from datetime import date, datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
@login_required
def index():
    subjects = Subject.query.filter_by(user_id=current_user.id, semester=current_user.current_semester).all()
    return render_template('attendance/index.html', subjects=subjects)

@attendance_bp.route('/attendance/add-subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code', '')
        credits = int(request.form.get('credits', 3))
        cia = int(request.form.get('cia_marks', 60))
        ese = int(request.form.get('ese_marks', 40))
        min_att = float(request.form.get('min_attendance', 75))
        color = request.form.get('color', '#6366f1')
        s = Subject(user_id=current_user.id, name=name, code=code,
                    semester=current_user.current_semester, credits=credits,
                    cia_marks=cia, ese_marks=ese, min_attendance=min_att, color=color)
        db.session.add(s)
        db.session.flush()
        from models.attendance import GradeRecord
        gr = GradeRecord(subject_id=s.id)
        db.session.add(gr)
        db.session.commit()
        flash(f'{name} added!', 'success')
        return redirect(url_for('attendance.index'))
    return render_template('attendance/add_subject.html')

@attendance_bp.route('/attendance/mark', methods=['POST'])
@login_required
def mark():
    subject_id = int(request.form.get('subject_id'))
    total = int(request.form.get('total', 1))
    attended = int(request.form.get('attended', 1))
    note = request.form.get('note', '')
    record_date = request.form.get('date', str(date.today()))
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    record = AttendanceRecord(subject_id=subject_id, total=total,
                              attended=attended, note=note,
                              date=datetime.strptime(record_date, '%Y-%m-%d').date())
    db.session.add(record)
    db.session.commit()
    return jsonify({'success': True, 'percentage': subject.attendance_percentage,
                    'status': subject.attendance_status,
                    'safe_to_miss': subject.safe_to_miss,
                    'classes_to_attend': subject.classes_to_attend})

@attendance_bp.route('/attendance/subject/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    records = AttendanceRecord.query.filter_by(subject_id=subject_id).order_by(AttendanceRecord.date.desc()).all()
    # Build forecast: next 30 classes
    forecast = []
    t = subject.total_classes
    a = subject.attended_classes
    for i in range(1, 16):
        attend_pct = round(((a + i) / (t + i)) * 100, 1)
        skip_pct = round((a / (t + i)) * 100, 1)
        forecast.append({'class': i, 'if_attend': attend_pct, 'if_skip': skip_pct})
    return render_template('attendance/detail.html', subject=subject, records=records, forecast=forecast)

@attendance_bp.route('/attendance/delete-record/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    record = AttendanceRecord.query.get_or_404(record_id)
    subject = Subject.query.filter_by(id=record.subject_id, user_id=current_user.id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True})

@attendance_bp.route('/attendance/bulk-update', methods=['POST'])
@login_required
def bulk_update():
    data = request.json
    for item in data.get('records', []):
        subject = Subject.query.filter_by(id=item['subject_id'], user_id=current_user.id).first()
        if subject:
            record = AttendanceRecord(subject_id=item['subject_id'],
                                      total=item['total'], attended=item['attended'],
                                      date=date.today())
            db.session.add(record)
    db.session.commit()
    return jsonify({'success': True})
