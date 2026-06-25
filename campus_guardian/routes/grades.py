from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.subject import Subject
from models.attendance import GradeRecord
from app import db

grades_bp = Blueprint('grades', __name__)

GRADE_POINTS = {'S': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'D': 4, 'F': 0}

@grades_bp.route('/grades')
@login_required
def index():
    subjects = Subject.query.filter_by(user_id=current_user.id, semester=current_user.current_semester).all()
    grade_data = []
    sgpa_sum = 0
    credit_sum = 0
    for s in subjects:
        gr = GradeRecord.query.filter_by(subject_id=s.id).first()
        if not gr:
            gr = GradeRecord(subject_id=s.id)
            db.session.add(gr)
            db.session.commit()
        grade, gp = gr.predicted_grade
        targets = {
            'S': gr.marks_needed_for_grade('S'),
            'A+': gr.marks_needed_for_grade('A+'),
            'A': gr.marks_needed_for_grade('A'),
            'B+': gr.marks_needed_for_grade('B+'),
        }
        grade_data.append({
            'subject': s, 'record': gr,
            'grade': grade, 'gp': gp,
            'predicted': gr.predicted_total, 'targets': targets
        })
        sgpa_sum += gp * s.credits
        credit_sum += s.credits

    predicted_sgpa = round(sgpa_sum / credit_sum, 2) if credit_sum > 0 else 0
    chart_labels = [d['subject'].name[:20] for d in grade_data]
    chart_predicted = [d['predicted'] for d in grade_data]
    chart_needed_s = [d['targets']['S'] or 0 for d in grade_data]

    return render_template('grades/index.html',
        grade_data=grade_data, predicted_sgpa=predicted_sgpa,
        chart_labels=chart_labels, chart_predicted=chart_predicted,
        chart_needed_s=chart_needed_s)

@grades_bp.route('/grades/update/<int:subject_id>', methods=['POST'])
@login_required
def update(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    gr = GradeRecord.query.filter_by(subject_id=subject_id).first()
    if not gr:
        gr = GradeRecord(subject_id=subject_id)
        db.session.add(gr)
    data = request.json
    gr.series_test1 = float(data.get('series_test1', 0))
    gr.series_test1_max = float(data.get('series_test1_max', 30))
    gr.series_test2 = float(data.get('series_test2', 0))
    gr.series_test2_max = float(data.get('series_test2_max', 30))
    gr.assignment = float(data.get('assignment', 0))
    gr.assignment_max = float(data.get('assignment_max', 10))
    gr.quiz = float(data.get('quiz', 0))
    gr.quiz_max = float(data.get('quiz_max', 10))
    gr.lab_marks = float(data.get('lab_marks', 0))
    gr.lab_marks_max = float(data.get('lab_marks_max', 10))
    gr.attendance_marks = float(data.get('attendance_marks', 0))
    gr.attendance_marks_max = float(data.get('attendance_marks_max', 10))
    gr.ese_marks = float(data.get('ese_marks', 0))
    gr.ese_max = float(data.get('ese_max', 40))
    db.session.commit()
    grade, gp = gr.predicted_grade
    return jsonify({
        'success': True,
        'predicted': gr.predicted_total,
        'grade': grade, 'gp': gp,
        'cia_total': gr.cia_total,
        'targets': {
            'S': gr.marks_needed_for_grade('S'),
            'A+': gr.marks_needed_for_grade('A+'),
            'A': gr.marks_needed_for_grade('A'),
            'B+': gr.marks_needed_for_grade('B+'),
        }
    })
