from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.subject import Subject
from models.attendance import TimetableEntry
from app import db
from datetime import date, timedelta

bunk_bp = Blueprint('bunk', __name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
PERIODS = [
    (1, '09:00', '10:00'), (2, '10:00', '11:00'), (3, '11:00', '12:00'),
    (4, '12:00', '13:00'), (5, '14:00', '15:00'), (6, '15:00', '16:00'),
    (7, '16:00', '17:00'), (8, '17:00', '18:00')
]

@bunk_bp.route('/bunk-planner')
@login_required
def index():
    subjects = Subject.query.filter_by(user_id=current_user.id, semester=current_user.current_semester).all()
    timetable = TimetableEntry.query.filter_by(user_id=current_user.id).all()
    timetable_grid = {}
    for day in range(6):
        timetable_grid[day] = {}
        for period in range(1, 9):
            timetable_grid[day][period] = None
    for entry in timetable:
        timetable_grid[entry.day_of_week][entry.period] = entry

    today = date.today()
    day_idx = today.weekday()
    today_classes = []
    if day_idx < 6:
        today_entries = TimetableEntry.query.filter_by(user_id=current_user.id, day_of_week=day_idx).all()
        for entry in today_entries:
            if entry.subject_id:
                subject = Subject.query.get(entry.subject_id)
                if subject:
                    safe = subject.safe_to_miss > 0
                    today_classes.append({
                        'period': entry.period, 'subject': subject,
                        'safe_to_skip': safe,
                        'attendance_pct': subject.attendance_percentage,
                        'status': subject.attendance_status,
                        'start': entry.start_time, 'end': entry.end_time
                    })

    # Weekly recommendations
    weekly_recs = []
    for day in range(6):
        day_entries = TimetableEntry.query.filter_by(user_id=current_user.id, day_of_week=day).all()
        day_data = {'day': DAYS[day], 'classes': [], 'skippable': 0, 'risky': 0}
        for entry in day_entries:
            if entry.subject_id:
                subject = Subject.query.get(entry.subject_id)
                if subject:
                    safe = subject.safe_to_miss > 0
                    day_data['classes'].append({'subject': subject.name[:20], 'safe': safe, 'period': entry.period})
                    if safe: day_data['skippable'] += 1
                    else: day_data['risky'] += 1
        if day_data['classes']:
            weekly_recs.append(day_data)

    # Forecast next 30 days
    forecast = []
    for s in subjects:
        t = s.total_classes
        a = s.attended_classes
        # Count upcoming classes in timetable (assume 4 weeks)
        day_idx_today = today.weekday()
        upcoming = 0
        for d in range(4 * 6):
            day = (day_idx_today + d) % 6
            count = TimetableEntry.query.filter_by(user_id=current_user.id, day_of_week=day, subject_id=s.id).count()
            upcoming += count
        pct_if_attend_all = round(((a + upcoming) / (t + upcoming)) * 100, 1) if (t + upcoming) > 0 else 0
        pct_if_skip_all = round((a / (t + upcoming)) * 100, 1) if (t + upcoming) > 0 else 0
        forecast.append({
            'subject': s, 'upcoming': upcoming,
            'if_attend_all': pct_if_attend_all,
            'if_skip_all': pct_if_skip_all,
            'current': s.attendance_percentage
        })

    return render_template('bunk/index.html',
        subjects=subjects, timetable_grid=timetable_grid,
        today_classes=today_classes, weekly_recs=weekly_recs,
        forecast=forecast, days=DAYS, periods=PERIODS,
        today_name=DAYS[min(day_idx, 5)])

@bunk_bp.route('/bunk-planner/timetable', methods=['POST'])
@login_required
def update_timetable():
    data = request.json
    # Clear existing
    TimetableEntry.query.filter_by(user_id=current_user.id).delete()
    for entry in data.get('entries', []):
        t = TimetableEntry(
            user_id=current_user.id,
            subject_id=entry.get('subject_id') or None,
            day_of_week=entry['day'],
            period=entry['period'],
            start_time=entry.get('start', '09:00'),
            end_time=entry.get('end', '10:00'),
            subject_name=entry.get('subject_name', '')
        )
        db.session.add(t)
    db.session.commit()
    return jsonify({'success': True})
