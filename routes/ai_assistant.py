from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.subject import Subject
from models.attendance import GradeRecord
import os
import json

ai_bp = Blueprint('ai', __name__)

def build_context(user):
    subjects = Subject.query.filter_by(user_id=user.id, semester=user.current_semester).all()
    context = f"Student: {user.name}, TKM College of Engineering Kollam, Semester {user.current_semester}, ECE/EEE program (KTU 2024 scheme).\n\n"
    context += "ATTENDANCE STATUS:\n"
    for s in subjects:
        gr = GradeRecord.query.filter_by(subject_id=s.id).first()
        grade_info = ""
        if gr:
            grade, gp = gr.predicted_grade
            grade_info = f", Predicted Grade: {grade} ({gr.predicted_total:.1f}/100)"
        context += f"- {s.name} ({s.code}): {s.attendance_percentage}% attendance ({s.attended_classes}/{s.total_classes} classes), Status: {s.attendance_status.upper()}, Safe to miss: {s.safe_to_miss} more classes{grade_info}\n"
    context += "\nKTU grading: S(90-100, 10GP), A+(80-89, 9GP), A(70-79, 8GP), B+(60-69, 7GP), B(50-59, 6GP). Minimum attendance: 75%.\n"
    context += "This student is also enrolled in IITM BS Data Science program (Diploma in DS + Diploma in Programming).\n"
    return context

@ai_bp.route('/ai/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    context = build_context(current_user)
    system_prompt = f"""You are Campus Guardian AI — a smart academic assistant for engineering students in India.
You have real-time data about this student:

{context}

Answer questions about:
- Attendance (which subjects are risky, how many classes can be missed, consecutive classes needed)
- Grades (predicted grades, marks needed for target grades, SGPA prediction)
- Study recommendations (which subject needs most attention)
- Bunk planning (safe vs unsafe to skip)
- IITM BS Data Science program advice
- KTU exam strategies

Be specific, use the actual data, give actionable advice. Keep responses concise and practical. Use emojis sparingly for readability. Format with bullet points when listing multiple items."""

    # Use Anthropic API (available in artifacts context)
    try:
        import urllib.request
        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': os.environ.get('ANTHROPIC_API_KEY', ''),
                'anthropic-version': '2023-06-01'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            reply = data['content'][0]['text']
            return jsonify({'reply': reply})
    except Exception as e:
        # Fallback: rule-based responses
        reply = generate_fallback_response(user_message, current_user)
        return jsonify({'reply': reply})

def generate_fallback_response(message, user):
    msg = message.lower()
    subjects = Subject.query.filter_by(user_id=user.id, semester=user.current_semester).all()
    if not subjects:
        return "You haven't added any subjects yet. Go to Attendance Guardian to add your S3 subjects!"

    critical = [s for s in subjects if s.attendance_status == 'critical']
    warning = [s for s in subjects if s.attendance_status == 'warning']
    safe = [s for s in subjects if s.attendance_status == 'safe']

    if any(w in msg for w in ['bunk', 'skip', 'miss', 'leave']):
        total_safe = sum(s.safe_to_miss for s in subjects)
        if critical:
            names = ', '.join(s.name[:20] for s in critical)
            return f"⚠️ **Do NOT skip any classes right now!**\n\n{len(critical)} subject(s) are in CRITICAL zone: {names}\n\nYou need to attend consecutively to recover. Safe to miss overall: **{total_safe} classes** across safe subjects only."
        elif warning:
            names = ', '.join(s.name[:20] for s in warning)
            return f"🟡 Be careful! {len(warning)} subject(s) in WARNING zone: {names}\n\nSafe to miss (safe subjects only): **{sum(s.safe_to_miss for s in safe)} classes**"
        else:
            return f"✅ All subjects are in safe zone!\n\nYou can safely miss:\n" + '\n'.join(f"- {s.name[:25]}: **{s.safe_to_miss} classes**" for s in subjects)

    elif any(w in msg for w in ['risky', 'risk', 'danger', 'critical', 'worst']):
        if critical:
            worst = min(subjects, key=lambda s: s.attendance_percentage)
            return f"🔴 Most at-risk subject: **{worst.name}**\n- Current attendance: {worst.attendance_percentage}%\n- Need to attend **{worst.classes_to_attend} consecutive classes** to reach 75%\n- Do NOT miss any more classes in this subject!"
        return f"✅ No critical subjects right now. Keep it up!"

    elif any(w in msg for w in ['grade', 'marks', 'sgpa', 'score']):
        grade_info = []
        for s in subjects:
            gr = GradeRecord.query.filter_by(subject_id=s.id).first()
            if gr and gr.predicted_total > 0:
                grade, gp = gr.predicted_grade
                grade_info.append(f"- {s.name[:25]}: **{grade}** ({gr.predicted_total:.1f}/100)")
        if grade_info:
            return "📊 **Predicted Grades:**\n" + '\n'.join(grade_info) + "\n\nUpdate your marks in Grade Predictor for more accurate predictions!"
        return "Enter your CIA marks in the Grade Predictor to see predictions!"

    elif any(w in msg for w in ['attend', 'week', 'today', 'tomorrow']):
        if critical:
            return f"📋 **This week, prioritize:**\n" + '\n'.join(f"- ⚠️ {s.name[:25]} (CRITICAL - {s.attendance_percentage}%)" for s in critical) + "\n\nAttend ALL classes in critical subjects without exception."
        return f"✅ Attendance looking good! Focus on maintaining above 85% in all subjects for maximum safety margin."

    else:
        return f"Hi {user.name}! I can help with:\n- 'Can I skip tomorrow?' → Bunk advice\n- 'Which subject is risky?' → Risk analysis\n- 'What grade will I get?' → Grade predictions\n- 'How many leaves can I take?' → Leave calculator\n\nWhat would you like to know?"
