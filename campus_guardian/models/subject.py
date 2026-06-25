from app import db
from datetime import datetime

class SubjectTemplate(db.Model):
    __tablename__ = 'subject_templates'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, default=3)
    cia_marks = db.Column(db.Integer, default=60)
    ese_marks = db.Column(db.Integer, default=40)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(20))
    name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, default=3)
    cia_marks = db.Column(db.Integer, default=60)
    ese_marks = db.Column(db.Integer, default=40)
    min_attendance = db.Column(db.Float, default=75.0)
    color = db.Column(db.String(7), default='#6366f1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy=True, cascade='all, delete-orphan')
    grade_records = db.relationship('GradeRecord', backref='subject', lazy=True, cascade='all, delete-orphan')

    @property
    def total_classes(self):
        return sum(r.total for r in self.attendance_records)

    @property
    def attended_classes(self):
        return sum(r.attended for r in self.attendance_records)

    @property
    def attendance_percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.attended_classes / self.total_classes) * 100, 2)

    @property
    def attendance_status(self):
        pct = self.attendance_percentage
        if pct >= 85:
            return 'safe'
        elif pct >= 75:
            return 'warning'
        else:
            return 'critical'

    @property
    def classes_to_attend(self):
        """Classes needed to reach min_attendance"""
        if self.attendance_percentage >= self.min_attendance:
            return 0
        t = self.total_classes
        a = self.attended_classes
        req = self.min_attendance / 100
        # solve: (a+x)/(t+x) >= req => x >= (req*t - a)/(1-req)
        if req >= 1:
            return float('inf')
        x = (req * t - a) / (1 - req)
        return max(0, int(x) + 1)

    @property
    def safe_to_miss(self):
        """Max classes can miss while staying above min_attendance"""
        t = self.total_classes
        a = self.attended_classes
        req = self.min_attendance / 100
        # solve: a/(t+x) >= req => x <= a/req - t
        if req == 0:
            return float('inf')
        max_total = int(a / req)
        return max(0, max_total - t)

    def __repr__(self):
        return f'<Subject {self.name}>'
