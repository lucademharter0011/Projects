export interface Timetable {
  id: number;
  user_id: User["id"];
  name: string;
  description?: string;
  semester: string;
  year: number;
  color_theme: string;
  is_active: boolean;
  courses: Course[];
}

export interface Course {
  id: number;
  timetable_id: Timetable["id"];
  name: string;
  code: string;
  instructor: string;
  room: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  course_type: string;
  credits: number;
  color: string;
  description?: string;
  horst_url?: string;
  moodle_url?: string;
  external_url?: string;
  is_active: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  password_hash: string;
  full_name: string;
  student_id?: string;
  created_at: string;
  timezone: string;
  notifications_enabled: boolean;
  theme_preference: string;
  timetables: Timetable[];
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  full_name: string;
  student_id?: string;
}
