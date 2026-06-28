from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.subject import Subject, SubjectTemplate
from models.attendance import GradeRecord
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def home():
    subjects = Subject.query.filter_by(user_id=current_user.id, semester=current_user.current_semester).all()
    total_subjects = len(subjects)
    safe = sum(1 for s in subjects if s.attendance_status == 'safe')
    warning = sum(1 for s in subjects if s.attendance_status == 'warning')
    critical = sum(1 for s in subjects if s.attendance_status == 'critical')

    # Overall attendance
    total_classes = sum(s.total_classes for s in subjects)
    attended = sum(s.attended_classes for s in subjects)
    overall_pct = round((attended / total_classes * 100), 1) if total_classes > 0 else 0

    # Grade summary
    grade_data = []
    sgpa_sum = 0
    credit_sum = 0
    for s in subjects:
        gr = GradeRecord.query.filter_by(subject_id=s.id).first()
        if gr:
            grade, gp = gr.predicted_grade
            grade_data.append({'subject': s.name[:25], 'grade': grade, 'gp': gp, 'marks': gr.predicted_total})
            sgpa_sum += gp * s.credits
            credit_sum += s.credits

    predicted_sgpa = round(sgpa_sum / credit_sum, 2) if credit_sum > 0 else 0

    chart_labels = [s.name[:15] + '...' if len(s.name) > 15 else s.name for s in subjects]
    chart_data = [s.attendance_percentage for s in subjects]
    chart_colors = ['#22c55e' if s.attendance_status == 'safe' else '#f59e0b' if s.attendance_status == 'warning' else '#ef4444' for s in subjects]

    return render_template('dashboard/home.html',
        subjects=subjects, total_subjects=total_subjects,
        safe=safe, warning=warning, critical=critical,
        overall_pct=overall_pct, total_classes=total_classes, attended=attended,
        grade_data=grade_data, predicted_sgpa=predicted_sgpa,
        chart_labels=chart_labels, chart_data=chart_data, chart_colors=chart_colors)

@dashboard_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    templates = SubjectTemplate.query.filter_by(semester=current_user.current_semester).all()
    if request.method == 'POST':
        selected = request.form.getlist('subjects')
        colors = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6']
        for i, sid in enumerate(selected):
            t = SubjectTemplate.query.get(int(sid))
            if t:
                existing = Subject.query.filter_by(user_id=current_user.id, code=t.code, semester=t.semester).first()
                if not existing:
                    s = Subject(user_id=current_user.id, code=t.code, name=t.name,
                                semester=t.semester, credits=t.credits,
                                cia_marks=t.cia_marks, ese_marks=t.ese_marks,
                                color=colors[i % len(colors)])
                    db.session.add(s)
                    gr = GradeRecord(subject_id=s.id) if False else None
        db.session.commit()
        # Create grade records
        new_subjects = Subject.query.filter_by(user_id=current_user.id, semester=current_user.current_semester).all()
        for s in new_subjects:
            if not GradeRecord.query.filter_by(subject_id=s.id).first():
                gr = GradeRecord(subject_id=s.id)
                db.session.add(gr)
        db.session.commit()
        flash('Subjects loaded! Welcome to your semester.', 'success')
        return redirect(url_for('dashboard.home'))
    return render_template('dashboard/setup.html', templates=templates)

@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.current_semester = int(request.form.get('semester', current_user.current_semester))
        db.session.commit()
        flash('Settings updated.', 'success')
    return render_template('dashboard/settings.html')
