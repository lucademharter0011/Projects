from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Timetable, Course, CourseSession, EnrolledCourse
from datetime import time
import json

course_catalog_bp = Blueprint('course_catalog', __name__)

# =================== COURSE CATALOG ===================

@course_catalog_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_course_catalog():
    """Alle verfügbaren Kurse abrufen (Kurskatalog)"""
    try:
        # Query parameters for filtering
        semester = request.args.get('semester')  # WS, SS, Both
        degree_program = request.args.get('degree_program')
        semester_level = request.args.get('semester_level', type=int)
        search = request.args.get('search')
        
        query = Course.query.filter_by(is_active=True)
        
        # Apply filters
        if semester:
            query = query.filter(Course.semester_offered.in_([semester, 'Both']))
        
        if degree_program:
            query = query.filter(Course.degree_program == degree_program)
        
        if semester_level:
            query = query.filter(Course.semester_level == semester_level)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Course.name.like(search_term),
                    Course.code.like(search_term),
                    Course.instructor.like(search_term)
                )
            )
        
        courses = query.order_by(Course.name).all()
        
        return jsonify({
            'courses': [course.to_dict(include_sessions=True) for course in courses],
            'count': len(courses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kurskatalog konnte nicht geladen werden: {str(e)}'}), 500

@course_catalog_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    """Detailierte Kursinformationen mit allen Terminen"""
    try:
        course = Course.query.filter_by(id=course_id, is_active=True).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        return jsonify({
            'course': course.to_dict(include_sessions=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kursdetails konnten nicht geladen werden: {str(e)}'}), 500

@course_catalog_bp.route('/courses/search', methods=['POST'])
@jwt_required()
def search_courses():
    """Erweiterte Kurssuche"""
    try:
        data = request.get_json()
        
        query = Course.query.filter_by(is_active=True)
        
        # Text search
        if data.get('search'):
            search_term = f"%{data['search']}%"
            query = query.filter(
                db.or_(
                    Course.name.like(search_term),
                    Course.code.like(search_term),
                    Course.instructor.like(search_term),
                    Course.description.like(search_term)
                )
            )
        
        # Multiple filters
        if data.get('degree_programs'):
            query = query.filter(Course.degree_program.in_(data['degree_programs']))
        
        if data.get('semester_levels'):
            query = query.filter(Course.semester_level.in_(data['semester_levels']))
        
        if data.get('course_types'):
            query = query.filter(Course.course_type.in_(data['course_types']))
        
        if data.get('instructors'):
            query = query.filter(Course.instructor.in_(data['instructors']))
        
        # Time filters
        if data.get('day_of_week') is not None:
            # Find courses that have sessions on specific days
            subquery = CourseSession.query.filter(
                CourseSession.day_of_week.in_(data['day_of_week'])
            ).subquery()
            query = query.join(subquery, Course.id == subquery.c.course_id)
        
        courses = query.order_by(Course.name).all()
        
        return jsonify({
            'courses': [course.to_dict(include_sessions=True) for course in courses],
            'count': len(courses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Suche fehlgeschlagen: {str(e)}'}), 500

# =================== COURSE ENROLLMENT ===================

@course_catalog_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course():
    """Kurs zum Stundenplan hinzufügen"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        required_fields = ['timetable_id', 'course_id', 'selected_sessions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} ist erforderlich'}), 400
        
        # Verify timetable belongs to user
        timetable = Timetable.query.filter_by(
            id=data['timetable_id'],
            user_id=current_user_id
        ).first()
        
        if not timetable:
            return jsonify({'error': 'Stundenplan nicht gefunden'}), 404
        
        # Verify course exists
        course = Course.query.filter_by(id=data['course_id'], is_active=True).first()
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        # Check if already enrolled
        existing_enrollment = EnrolledCourse.query.filter_by(
            timetable_id=data['timetable_id'],
            course_id=data['course_id']
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Bereits für diesen Kurs eingetragen'}), 400
        
        # Validate selected sessions
        if not data['selected_sessions']:
            return jsonify({'error': 'Mindestens eine Session auswählen'}), 400
        
        session_ids = data['selected_sessions']
        sessions = CourseSession.query.filter(
            CourseSession.id.in_(session_ids),
            CourseSession.course_id == data['course_id']
        ).all()
        
        if len(sessions) != len(session_ids):
            return jsonify({'error': 'Ungültige Session-Auswahl'}), 400
        
        # Check for time conflicts
        conflicts = check_time_conflicts(timetable.id, sessions)
        if conflicts:
            return jsonify({
                'error': 'Zeitkonflikt erkannt',
                'conflicts': conflicts
            }), 400
        
        # Create enrollment
        enrollment = EnrolledCourse(
            timetable_id=data['timetable_id'],
            course_id=data['course_id'],
            selected_sessions=json.dumps(session_ids),
            custom_color=data.get('custom_color'),
            reminder_enabled=data.get('reminder_enabled', True),
            reminder_minutes=data.get('reminder_minutes', 15)
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': f'Erfolgreich für "{course.name}" eingetragen',
            'enrollment': enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Einschreibung fehlgeschlagen: {str(e)}'}), 500

@course_catalog_bp.route('/enrollment/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def update_enrollment(enrollment_id):
    """Kurs-Einschreibung bearbeiten (Sessions ändern)"""
    try:
        current_user_id = get_jwt_identity()
        
        enrollment = EnrolledCourse.query.join(Timetable).filter(
            EnrolledCourse.id == enrollment_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Einschreibung nicht gefunden'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        # Update selected sessions
        if 'selected_sessions' in data:
            if not data['selected_sessions']:
                return jsonify({'error': 'Mindestens eine Session auswählen'}), 400
            
            session_ids = data['selected_sessions']
            sessions = CourseSession.query.filter(
                CourseSession.id.in_(session_ids),
                CourseSession.course_id == enrollment.course_id
            ).all()
            
            if len(sessions) != len(session_ids):
                return jsonify({'error': 'Ungültige Session-Auswahl'}), 400
            
            # Check for conflicts (excluding current enrollment)
            conflicts = check_time_conflicts(enrollment.timetable_id, sessions, exclude_enrollment_id=enrollment_id)
            if conflicts:
                return jsonify({
                    'error': 'Zeitkonflikt erkannt',
                    'conflicts': conflicts
                }), 400
            
            enrollment.selected_sessions = json.dumps(session_ids)
        
        # Update other fields
        if 'custom_color' in data:
            enrollment.custom_color = data['custom_color']
        if 'reminder_enabled' in data:
            enrollment.reminder_enabled = data['reminder_enabled']
        if 'reminder_minutes' in data:
            enrollment.reminder_minutes = data['reminder_minutes']
        if 'is_active' in data:
            enrollment.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Einschreibung erfolgreich aktualisiert',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update fehlgeschlagen: {str(e)}'}), 500

@course_catalog_bp.route('/enrollment/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def unenroll_from_course(enrollment_id):
    """Aus Kurs austragen"""
    try:
        current_user_id = get_jwt_identity()
        
        enrollment = EnrolledCourse.query.join(Timetable).filter(
            EnrolledCourse.id == enrollment_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Einschreibung nicht gefunden'}), 404
        
        course_name = enrollment.course.name
        
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': f'Erfolgreich aus "{course_name}" ausgetragen'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Austragung fehlgeschlagen: {str(e)}'}), 500

# =================== TIMETABLE WITH ENROLLMENTS ===================

@course_catalog_bp.route('/timetable/<int:timetable_id>/schedule', methods=['GET'])
@jwt_required()
def get_timetable_schedule(timetable_id):
    """Stundenplan mit allen eingetragenen Kursen und deren Terminen"""
    try:
        current_user_id = get_jwt_identity()
        
        timetable = Timetable.query.filter_by(
            id=timetable_id,
            user_id=current_user_id
        ).first()
        
        if not timetable:
            return jsonify({'error': 'Stundenplan nicht gefunden'}), 404
        
        # Get all active enrollments
        enrollments = EnrolledCourse.query.filter_by(
            timetable_id=timetable_id,
            is_active=True
        ).all()
        
        # Build schedule data
        schedule_items = []
        
        for enrollment in enrollments:
            if enrollment.selected_sessions:
                session_ids = json.loads(enrollment.selected_sessions)
                sessions = CourseSession.query.filter(
                    CourseSession.id.in_(session_ids)
                ).all()
                
                for session in sessions:
                    schedule_items.append({
                        'enrollment_id': enrollment.id,
                        'course': enrollment.course.to_dict(),
                        'session': session.to_dict(),
                        'custom_color': enrollment.custom_color,
                        'reminder_enabled': enrollment.reminder_enabled,
                        'reminder_minutes': enrollment.reminder_minutes
                    })
        
        return jsonify({
            'timetable': timetable.to_dict(),
            'schedule_items': schedule_items,
            'count': len(schedule_items)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Stundenplan konnte nicht geladen werden: {str(e)}'}), 500

# =================== UTILITY FUNCTIONS ===================

def check_time_conflicts(timetable_id, new_sessions, exclude_enrollment_id=None):
    """Prüft auf Zeitkonflikte mit bestehenden Einschreibungen"""
    conflicts = []
    
    # Get existing enrollments
    query = EnrolledCourse.query.filter_by(
        timetable_id=timetable_id,
        is_active=True
    )
    
    if exclude_enrollment_id:
        query = query.filter(EnrolledCourse.id != exclude_enrollment_id)
    
    existing_enrollments = query.all()
    
    # Get all existing sessions
    existing_sessions = []
    for enrollment in existing_enrollments:
        if enrollment.selected_sessions:
            session_ids = json.loads(enrollment.selected_sessions)
            sessions = CourseSession.query.filter(
                CourseSession.id.in_(session_ids)
            ).all()
            existing_sessions.extend(sessions)
    
    # Check conflicts
    for new_session in new_sessions:
        for existing_session in existing_sessions:
            if (new_session.day_of_week == existing_session.day_of_week and
                not (new_session.end_time <= existing_session.start_time or 
                     new_session.start_time >= existing_session.end_time)):
                
                conflicts.append({
                    'new_session': {
                        'course': new_session.course.name,
                        'session_type': new_session.session_type,
                        'time': f"{new_session.start_time.strftime('%H:%M')}-{new_session.end_time.strftime('%H:%M')}"
                    },
                    'existing_session': {
                        'course': existing_session.course.name,
                        'session_type': existing_session.session_type,
                        'time': f"{existing_session.start_time.strftime('%H:%M')}-{existing_session.end_time.strftime('%H:%M')}"
                    }
                })
    
    return conflicts

# =================== COURSE MANAGEMENT (Admin) ===================

@course_catalog_bp.route('/admin/courses', methods=['POST'])
@jwt_required()
def create_course():
    """Neuen Kurs zum Katalog hinzufügen (Admin)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        required_fields = ['name', 'code']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} ist erforderlich'}), 400
        
        # Check if course code already exists
        if Course.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Kurscode bereits vergeben'}), 400
        
        # Create course
        course = Course(
            name=data['name'],
            code=data['code'],
            instructor=data.get('instructor'),
            description=data.get('description'),
            credits=data.get('credits'),
            course_type=data.get('course_type', 'Vorlesung'),
            semester_offered=data.get('semester_offered'),
            degree_program=data.get('degree_program'),
            semester_level=data.get('semester_level'),
            horst_url=data.get('horst_url'),
            moodle_url=data.get('moodle_url'),
            syllabus_url=data.get('syllabus_url')
        )
        
        db.session.add(course)
        db.session.flush()  # Get course ID
        
        # Add sessions if provided
        if data.get('sessions'):
            for session_data in data['sessions']:
                session = CourseSession(
                    course_id=course.id,
                    session_type=session_data.get('session_type', 'Vorlesung'),
                    group_name=session_data.get('group_name'),
                    day_of_week=session_data['day_of_week'],
                    start_time=time.fromisoformat(session_data['start_time']),
                    end_time=time.fromisoformat(session_data['end_time']),
                    room=session_data.get('room'),
                    weeks=session_data.get('weeks'),
                    color=session_data.get('color', '#3498db')
                )
                db.session.add(session)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kurs erfolgreich erstellt',
            'course': course.to_dict(include_sessions=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kurs konnte nicht erstellt werden: {str(e)}'}), 500

@course_catalog_bp.route('/admin/courses/<int:course_id>/sessions', methods=['POST'])
@jwt_required()
def add_course_session(course_id):
    """Session zu einem Kurs hinzufügen"""
    try:
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        required_fields = ['day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} ist erforderlich'}), 400
        
        session = CourseSession(
            course_id=course_id,
            session_type=data.get('session_type', 'Vorlesung'),
            group_name=data.get('group_name'),
            day_of_week=data['day_of_week'],
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            room=data.get('room'),
            weeks=data.get('weeks'),
            color=data.get('color', course.course_sessions[0].color if course.course_sessions else '#3498db')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Session erfolgreich hinzugefügt',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Session konnte nicht erstellt werden: {str(e)}'}), 500