from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Timetable, Course, CourseComment, EnrolledCourse, CourseSession
from datetime import datetime, time
from sqlalchemy import or_, and_

courses_bp = Blueprint('courses', __name__)

def validate_time_format(time_str):
    """Zeit-Format validieren (HH:MM)"""
    try:
        time.fromisoformat(time_str)
        return True
    except:
        return False

def parse_time(time_str):
    """Zeit-String zu time Objekt konvertieren"""
    try:
        return time.fromisoformat(time_str)
    except:
        return None

# =================== COURSE CATALOG ENDPOINTS ===================

@courses_bp.route('/catalog', methods=['GET'])
@jwt_required()
def get_course_catalog():
    """Course Catalog API - Alle verfügbaren Kurse abrufen"""
    try:
        # Get query parameters
        search_query = request.args.get('search', '')
        course_type = request.args.get('type', '')
        instructor = request.args.get('instructor', '')
        day_of_week = request.args.get('day', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Base query
        query = Course.query

        # Apply filters
        if search_query:
            query = query.filter(
                or_(
                    Course.name.ilike(f'%{search_query}%'),
                    Course.code.ilike(f'%{search_query}%'),
                    Course.description.ilike(f'%{search_query}%')
                )
            )

        if course_type:
            query = query.filter(Course.course_type.ilike(f'%{course_type}%'))

        if instructor:
            query = query.filter(Course.instructor.ilike(f'%{instructor}%'))

        if day_of_week:
            try:
                day_num = int(day_of_week)
                if 0 <= day_num <= 6:
                    query = query.filter(Course.day_of_week == day_num)
            except ValueError:
                pass

        # Get active courses only
        query = query.filter(Course.is_active == True)

        # Pagination
        paginated_courses = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        # Prepare response
        courses_data = []
        for course in paginated_courses.items:
            course_dict = course.to_dict()
            
            # Add additional info
            course_dict['available'] = True
            course_dict['enrollment_count'] = EnrolledCourse.query.filter_by(
                course_id=course.id, 
                status='active'
            ).count()
            
            courses_data.append(course_dict)

        return jsonify({
            'success': True,
            'courses': courses_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_courses.total,
                'pages': paginated_courses.pages,
                'has_next': paginated_courses.has_next,
                'has_prev': paginated_courses.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler beim Laden des Kurskatalogs',
            'details': str(e)
        }), 500


@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """In Kurs einschreiben"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if course exists
        course = Course.query.get_or_404(course_id)
        
        # Check if already enrolled
        existing_enrollment = EnrolledCourse.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).first()

        if existing_enrollment:
            if existing_enrollment.status == 'active':
                return jsonify({
                    'success': False,
                    'error': 'Bereits in diesem Kurs eingeschrieben'
                }), 400
            else:
                # Reactivate enrollment
                existing_enrollment.status = 'active'
                existing_enrollment.enrollment_date = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Erfolgreich wieder eingeschrieben',
                    'enrollment': existing_enrollment.to_dict()
                }), 200

        # Create new enrollment
        new_enrollment = EnrolledCourse(
            user_id=current_user_id,
            course_id=course_id,
            enrollment_date=datetime.utcnow(),
            status='active'
        )

        db.session.add(new_enrollment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Erfolgreich eingeschrieben',
            'enrollment': new_enrollment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Fehler bei der Einschreibung',
            'details': str(e)
        }), 500


@courses_bp.route('/<int:course_id>/unenroll', methods=['POST'])
@jwt_required()
def unenroll_from_course(course_id):
    """Aus Kurs austragen"""
    try:
        current_user_id = get_jwt_identity()
        
        enrollment = EnrolledCourse.query.filter_by(
            user_id=current_user_id,
            course_id=course_id,
            status='active'
        ).first()

        if not enrollment:
            return jsonify({
                'success': False,
                'error': 'Nicht in diesem Kurs eingeschrieben'
            }), 400

        enrollment.status = 'dropped'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Erfolgreich ausgetragen'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Fehler beim Austragen',
            'details': str(e)
        }), 500


@courses_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Meine eingeschriebenen Kurse abrufen"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get enrolled courses
        enrollments = db.session.query(EnrolledCourse, Course).join(
            Course, EnrolledCourse.course_id == Course.id
        ).filter(
            EnrolledCourse.user_id == current_user_id,
            EnrolledCourse.status == 'active'
        ).all()

        courses_data = []
        for enrollment, course in enrollments:
            course_dict = course.to_dict()
            course_dict['enrollment'] = enrollment.to_dict()
            courses_data.append(course_dict)

        return jsonify({
            'success': True,
            'courses': courses_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler beim Laden der Kurse',
            'details': str(e)
        }), 500


@courses_bp.route('/<int:course_id>/sessions', methods=['GET'])
@jwt_required()
def get_course_sessions(course_id):
    """Kurssitzungen abrufen"""
    try:
        # Check if user has access to course
        current_user_id = get_jwt_identity()
        
        enrollment = EnrolledCourse.query.filter_by(
            user_id=current_user_id,
            course_id=course_id,
            status='active'
        ).first()

        if not enrollment:
            return jsonify({
                'success': False,
                'error': 'Nicht berechtigt, diese Kurssitzungen zu sehen'
            }), 403

        # Get sessions
        sessions = CourseSession.query.filter_by(
            course_id=course_id
        ).order_by(CourseSession.session_date).all()

        sessions_data = [session.to_dict() for session in sessions]

        return jsonify({
            'success': True,
            'sessions': sessions_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler beim Laden der Kurssitzungen',
            'details': str(e)
        }), 500

# =================== EXISTING TIMETABLE COURSE ENDPOINTS ===================

@courses_bp.route('/timetable/<int:timetable_id>', methods=['GET'])
@jwt_required()
def get_timetable_courses(timetable_id):
    """Alle Kurse eines Stundenplans abrufen"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify timetable belongs to user
        timetable = Timetable.query.filter_by(
            id=timetable_id, 
            user_id=current_user_id
        ).first()
        
        if not timetable:
            return jsonify({'error': 'Stundenplan nicht gefunden'}), 404
        
        courses = Course.query.filter_by(timetable_id=timetable_id).all()
        
        return jsonify({
            'courses': [course.to_dict() for course in courses],
            'count': len(courses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kurse konnten nicht geladen werden: {str(e)}'}), 500

@courses_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    """Neuen Kurs erstellen"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        # Validate required fields
        required_fields = ['timetable_id', 'name', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} ist erforderlich'}), 400
        
        # Verify timetable belongs to user
        timetable = Timetable.query.filter_by(
            id=data['timetable_id'], 
            user_id=current_user_id
        ).first()
        
        if not timetable:
            return jsonify({'error': 'Stundenplan nicht gefunden'}), 404
        
        # Validate time format
        start_time = parse_time(data['start_time'])
        end_time = parse_time(data['end_time'])
        
        if not start_time or not end_time:
            return jsonify({'error': 'Ungültiges Zeitformat (verwenden Sie HH:MM)'}), 400
        
        if start_time >= end_time:
            return jsonify({'error': 'Startzeit muss vor Endzeit liegen'}), 400
        
        # Validate day_of_week
        if not (0 <= data['day_of_week'] <= 6):
            return jsonify({'error': 'Wochentag muss zwischen 0 (Montag) und 6 (Sonntag) liegen'}), 400
        
        # Check for time conflicts
        existing_courses = Course.query.filter_by(
            timetable_id=data['timetable_id'],
            day_of_week=data['day_of_week']
        ).all()
        
        for course in existing_courses:
            if not (end_time <= course.start_time or start_time >= course.end_time):
                return jsonify({
                    'error': f'Zeitkonflikt mit Kurs "{course.name}" ({course.start_time.strftime("%H:%M")}-{course.end_time.strftime("%H:%M")})'
                }), 400
        
        # Create new course
        course = Course(
            timetable_id=data['timetable_id'],
            name=data['name'],
            code=data.get('code'),
            instructor=data.get('instructor'),
            room=data.get('room'),
            description=data.get('description'),
            color=data.get('color', '#3498db'),
            day_of_week=data['day_of_week'],
            start_time=start_time,
            end_time=end_time,
            course_type=data.get('course_type', 'Vorlesung'),
            credits=data.get('credits'),
            horst_url=data.get('horst_url'),
            moodle_url=data.get('moodle_url'),
            external_url=data.get('external_url'),
            reminder_enabled=data.get('reminder_enabled', True),
            reminder_minutes=data.get('reminder_minutes', 15)
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Kurs erfolgreich erstellt',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kurs konnte nicht erstellt werden: {str(e)}'}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Spezifischen Kurs mit Details abrufen"""
    try:
        current_user_id = get_jwt_identity()
        
        course = Course.query.join(Timetable).filter(
            Course.id == course_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        # Get course sessions for catalog view
        sessions = CourseSession.query.filter_by(course_id=course_id).order_by(CourseSession.session_date).all()
        
        # Get enrollment info
        enrollment = EnrolledCourse.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).first()

        course_data = course.to_dict(include_comments=True)
        course_data['sessions'] = [session.to_dict() for session in sessions]
        course_data['is_enrolled'] = enrollment is not None
        course_data['enrollment_status'] = enrollment.status if enrollment else None
        
        return jsonify({
            'course': course_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kurs konnte nicht geladen werden: {str(e)}'}), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """Kurs aktualisieren"""
    try:
        current_user_id = get_jwt_identity()
        
        course = Course.query.join(Timetable).filter(
            Course.id == course_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        # Update basic fields
        if 'name' in data:
            course.name = data['name']
        if 'code' in data:
            course.code = data['code']
        if 'instructor' in data:
            course.instructor = data['instructor']
        if 'room' in data:
            course.room = data['room']
        if 'description' in data:
            course.description = data['description']
        if 'color' in data:
            course.color = data['color']
        if 'course_type' in data:
            course.course_type = data['course_type']
        if 'credits' in data:
            course.credits = data['credits']
        if 'horst_url' in data:
            course.horst_url = data['horst_url']
        if 'moodle_url' in data:
            course.moodle_url = data['moodle_url']
        if 'external_url' in data:
            course.external_url = data['external_url']
        if 'is_active' in data:
            course.is_active = data['is_active']
        if 'reminder_enabled' in data:
            course.reminder_enabled = data['reminder_enabled']
        if 'reminder_minutes' in data:
            course.reminder_minutes = data['reminder_minutes']
        
        # Handle time updates
        time_changed = False
        new_start_time = course.start_time
        new_end_time = course.end_time
        new_day = course.day_of_week
        
        if 'start_time' in data:
            new_start_time = parse_time(data['start_time'])
            if not new_start_time:
                return jsonify({'error': 'Ungültiges Startzeit-Format'}), 400
            time_changed = True
        
        if 'end_time' in data:
            new_end_time = parse_time(data['end_time'])
            if not new_end_time:
                return jsonify({'error': 'Ungültiges Endzeit-Format'}), 400
            time_changed = True
        
        if 'day_of_week' in data:
            if not (0 <= data['day_of_week'] <= 6):
                return jsonify({'error': 'Ungültiger Wochentag'}), 400
            new_day = data['day_of_week']
            time_changed = True
        
        # Validate time logic
        if new_start_time >= new_end_time:
            return jsonify({'error': 'Startzeit muss vor Endzeit liegen'}), 400
        
        # Check for conflicts if time changed
        if time_changed:
            existing_courses = Course.query.filter_by(
                timetable_id=course.timetable_id,
                day_of_week=new_day
            ).filter(Course.id != course_id).all()
            
            for existing_course in existing_courses:
                if not (new_end_time <= existing_course.start_time or new_start_time >= existing_course.end_time):
                    return jsonify({
                        'error': f'Zeitkonflikt mit Kurs "{existing_course.name}"'
                    }), 400
        
        # Apply time changes
        course.start_time = new_start_time
        course.end_time = new_end_time
        course.day_of_week = new_day
        course.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kurs erfolgreich aktualisiert',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kurs konnte nicht aktualisiert werden: {str(e)}'}), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """Kurs löschen"""
    try:
        current_user_id = get_jwt_identity()
        
        course = Course.query.join(Timetable).filter(
            Course.id == course_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Kurs erfolgreich gelöscht'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kurs konnte nicht gelöscht werden: {str(e)}'}), 500

# =================== COURSE COMMENTS ===================

@courses_bp.route('/<int:course_id>/comments', methods=['GET'])
@jwt_required()
def get_course_comments(course_id):
    """Kommentare eines Kurses abrufen"""
    try:
        current_user_id = get_jwt_identity()
        
        course = Course.query.join(Timetable).filter(
            Course.id == course_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        comments = CourseComment.query.filter_by(course_id=course_id).all()
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments],
            'count': len(comments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Kommentare konnten nicht geladen werden: {str(e)}'}), 500

@courses_bp.route('/<int:course_id>/comments', methods=['POST'])
@jwt_required()
def create_course_comment(course_id):
    """Kommentar zu einem Kurs hinzufügen"""
    try:
        current_user_id = get_jwt_identity()
        
        course = Course.query.join(Timetable).filter(
            Course.id == course_id,
            Timetable.user_id == current_user_id
        ).first()
        
        if not course:
            return jsonify({'error': 'Kurs nicht gefunden'}), 404
        
        data = request.get_json()
        if not data or not data.get('comment'):
            return jsonify({'error': 'Kommentar ist erforderlich'}), 400
        
        comment = CourseComment(
            course_id=course_id,
            user_id=current_user_id,
            comment=data['comment'],
            comment_type=data.get('comment_type', 'note'),
            is_private=data.get('is_private', True)
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Kommentar erfolgreich hinzugefügt',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kommentar konnte nicht erstellt werden: {str(e)}'}), 500

@courses_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_course_comment(comment_id):
    """Kommentar aktualisieren"""
    try:
        current_user_id = get_jwt_identity()
        
        comment = CourseComment.query.filter_by(
            id=comment_id,
            user_id=current_user_id
        ).first()
        
        if not comment:
            return jsonify({'error': 'Kommentar nicht gefunden'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten empfangen'}), 400
        
        if 'comment' in data:
            comment.comment = data['comment']
        if 'comment_type' in data:
            comment.comment_type = data['comment_type']
        if 'is_private' in data:
            comment.is_private = data['is_private']
        
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Kommentar erfolgreich aktualisiert',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kommentar konnte nicht aktualisiert werden: {str(e)}'}), 500

@courses_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_course_comment(comment_id):
    """Kommentar löschen"""
    try:
        current_user_id = get_jwt_identity()
        
        comment = CourseComment.query.filter_by(
            id=comment_id,
            user_id=current_user_id
        ).first()
        
        if not comment:
            return jsonify({'error': 'Kommentar nicht gefunden'}), 404
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Kommentar erfolgreich gelöscht'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Kommentar konnte nicht gelöscht werden: {str(e)}'}), 500

# =================== ADDITIONAL CATALOG UTILITY ENDPOINTS ===================

@courses_bp.route('/search', methods=['POST'])
@jwt_required()
def search_courses():
    """Erweiterte Kurssuche"""
    try:
        data = request.get_json()
        
        # Search parameters
        search_term = data.get('search', '')
        filters = data.get('filters', {})
        
        query = Course.query.filter(Course.is_active == True)

        # Text search
        if search_term:
            query = query.filter(
                or_(
                    Course.name.ilike(f'%{search_term}%'),
                    Course.code.ilike(f'%{search_term}%'),
                    Course.instructor.ilike(f'%{search_term}%'),
                    Course.description.ilike(f'%{search_term}%')
                )
            )

        # Apply filters
        if filters.get('course_type'):
            query = query.filter(Course.course_type == filters['course_type'])
            
        if filters.get('day_of_week') is not None:
            query = query.filter(Course.day_of_week == filters['day_of_week'])
            
        if filters.get('time_range'):
            start_time = time.fromisoformat(filters['time_range']['start'])
            end_time = time.fromisoformat(filters['time_range']['end'])
            query = query.filter(
                and_(
                    Course.start_time >= start_time,
                    Course.end_time <= end_time
                )
            )

        if filters.get('credits'):
            query = query.filter(Course.credits == filters['credits'])

        # Execute query
        courses = query.limit(50).all()
        courses_data = [course.to_dict() for course in courses]

        return jsonify({
            'success': True,
            'courses': courses_data,
            'count': len(courses_data)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler bei der Suche',
            'details': str(e)
        }), 500


@courses_bp.route('/types', methods=['GET'])
@jwt_required()
def get_course_types():
    """Verfügbare Kurstypen abrufen"""
    try:
        # Get distinct course types
        course_types = db.session.query(Course.course_type).distinct().filter(
            Course.course_type.isnot(None),
            Course.is_active == True
        ).all()

        types_list = [ct[0] for ct in course_types if ct[0]]

        return jsonify({
            'success': True,
            'course_types': types_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler beim Laden der Kurstypen',
            'details': str(e)
        }), 500


@courses_bp.route('/instructors', methods=['GET'])
@jwt_required()
def get_instructors():
    """Verfügbare Dozenten abrufen"""
    try:
        # Get distinct instructors
        instructors = db.session.query(Course.instructor).distinct().filter(
            Course.instructor.isnot(None),
            Course.is_active == True
        ).all()

        instructors_list = [inst[0] for inst in instructors if inst[0]]

        return jsonify({
            'success': True,
            'instructors': instructors_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Fehler beim Laden der Dozenten',
            'details': str(e)
        }), 500