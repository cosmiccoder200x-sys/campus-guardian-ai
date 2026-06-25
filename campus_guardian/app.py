from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'campus-guardian-secret-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///campus_guardian.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access Campus Guardian.'

    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.attendance import attendance_bp
    from routes.grades import grades_bp
    from routes.bunk import bunk_bp
    from routes.ai_assistant import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(bunk_bp)
    app.register_blueprint(ai_bp)

    with app.app_context():
        db.create_all()
        try:
            seed_default_subjects()
        except Exception as e:
            print(f"Seed warning: {e}")

    return app

def seed_default_subjects():
    from models.subject import SubjectTemplate
    if SubjectTemplate.query.count() == 0:
        subjects = [
            # S3
            SubjectTemplate(code='24MAP301', name='Advanced Linear Algebra, Complex Analysis & PDE', semester=3, credits=5, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24EST332', name='Network Theory', semester=3, credits=5, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERJ303', name='Digital Electronics and Logic Design', semester=3, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERP304', name='Data Structures and Algorithms', semester=3, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERT305', name='Sensor & Sensor Circuits', semester=3, credits=3, cia_marks=40, ese_marks=60),
            SubjectTemplate(code='24HUT310', name='Life Skills and Professional Ethics', semester=3, credits=3, cia_marks=40, ese_marks=60),
            SubjectTemplate(code='24ESP307', name='System Simulation & Virtual Instrumentation Lab', semester=3, credits=2, cia_marks=100, ese_marks=0),
            # S4
            SubjectTemplate(code='24ERT401', name='Computer Organization and Architecture', semester=4, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERT402', name='Signals & Systems', semester=4, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERP403', name='Electrical Technology', semester=4, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERJ404', name='Solid State Electronic Devices and Circuits', semester=4, credits=5, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24HUT435', name='Engineering Economics', semester=4, credits=3, cia_marks=40, ese_marks=60),
            SubjectTemplate(code='24ERP407', name='Object Oriented Programming Using Java', semester=4, credits=2, cia_marks=60, ese_marks=40),
            # S5
            SubjectTemplate(code='24ERT501', name='Control Systems', semester=5, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERJ502', name='Database Management Systems', semester=5, credits=5, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERT503', name='Artificial Intelligence: Theory and Applications', semester=5, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERP504', name='Operating Systems', semester=5, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24HUT535', name='Project Management and Finance', semester=5, credits=3, cia_marks=40, ese_marks=60),
            SubjectTemplate(code='24ERT507', name='Software Engineering', semester=5, credits=2, cia_marks=60, ese_marks=40),
            # S6
            SubjectTemplate(code='24ERP601', name='Computer Networks', semester=6, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERP602', name='Embedded System Design and IoT', semester=6, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERT603', name='Power Electronics & Drives', semester=6, credits=3, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERS606', name='Seminar', semester=6, credits=2, cia_marks=100, ese_marks=0),
            # S7
            SubjectTemplate(code='24ERP701', name='Computer Vision', semester=7, credits=4, cia_marks=60, ese_marks=40),
            SubjectTemplate(code='24ERP702', name='Energy Systems', semester=7, credits=4, cia_marks=60, ese_marks=40),
            # S8
            SubjectTemplate(code='24ERD804', name='Major Project / Internship', semester=8, credits=7, cia_marks=100, ese_marks=0),
        ]
        db.session.bulk_save_objects(subjects)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
