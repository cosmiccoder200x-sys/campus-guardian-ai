from app import db
from datetime import datetime

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Integer, default=1)
    attended = db.Column(db.Integer, default=1)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GradeRecord(db.Model):
    __tablename__ = 'grade_records'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    # CIA components
    series_test1 = db.Column(db.Float, default=0)
    series_test1_max = db.Column(db.Float, default=30)
    series_test2 = db.Column(db.Float, default=0)
    series_test2_max = db.Column(db.Float, default=30)
    assignment = db.Column(db.Float, default=0)
    assignment_max = db.Column(db.Float, default=10)
    quiz = db.Column(db.Float, default=0)
    quiz_max = db.Column(db.Float, default=10)
    lab_marks = db.Column(db.Float, default=0)
    lab_marks_max = db.Column(db.Float, default=10)
    attendance_marks = db.Column(db.Float, default=0)
    attendance_marks_max = db.Column(db.Float, default=10)
    # ESE
    ese_marks = db.Column(db.Float, default=0)
    ese_max = db.Column(db.Float, default=40)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def cia_total(self):
        return (self.series_test1 + self.series_test2 + self.assignment +
                self.quiz + self.lab_marks + self.attendance_marks)

    @property
    def cia_max(self):
        return (self.series_test1_max + self.series_test2_max + self.assignment_max +
                self.quiz_max + self.lab_marks_max + self.attendance_marks_max)

    @property
    def predicted_total(self):
        subject = self.subject
        cia_weight = subject.cia_marks
        ese_weight = subject.ese_marks
        total_weight = cia_weight + ese_weight
        if self.cia_max == 0:
            return 0
        cia_scaled = (self.cia_total / self.cia_max) * cia_weight
        ese_scaled = (self.ese_marks / self.ese_max) * ese_weight if self.ese_max > 0 else 0
        return round(cia_scaled + ese_scaled, 2)

    @property
    def predicted_grade(self):
        pct = self.predicted_total
        if pct >= 90: return ('S', 10)
        elif pct >= 80: return ('A+', 9)
        elif pct >= 70: return ('A', 8)
        elif pct >= 60: return ('B+', 7)
        elif pct >= 50: return ('B', 6)
        elif pct >= 45: return ('C', 5)
        elif pct >= 40: return ('D', 4)
        else: return ('F', 0)

    def marks_needed_for_grade(self, target_grade):
        grade_map = {'S': 90, 'A+': 80, 'A': 70, 'B+': 60, 'B': 50}
        target_pct = grade_map.get(target_grade, 50)
        subject = self.subject
        cia_weight = subject.cia_marks
        ese_weight = subject.ese_marks
        if self.cia_max == 0 or ese_weight == 0:
            return None
        cia_scaled = (self.cia_total / self.cia_max) * cia_weight
        needed_total = target_pct
        needed_ese_scaled = needed_total - cia_scaled
        needed_ese = (needed_ese_scaled / ese_weight) * self.ese_max
        return round(max(0, min(needed_ese, self.ese_max)), 2)


class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Mon, 6=Sun
    period = db.Column(db.Integer, nullable=False)  # 1-8
    start_time = db.Column(db.String(5), default='09:00')
    end_time = db.Column(db.String(5), default='10:00')
    subject_name = db.Column(db.String(200))

    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
