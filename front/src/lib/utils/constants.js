// front/src/lib/utils/constants.js
export const APP_NAME = '249Sudan';

export const ROLES = {
	STUDENT: 'student',
	TEACHER: 'teacher',
	MODERATOR: 'moderator',
	MANAGER: 'manager'
};

export const COURSE_STATUS = {
	DRAFT: 'draft',
	PUBLISHED: 'published',
	ARCHIVED: 'archived'
};

export const ENROLLMENT_STATUS = {
	ENROLLED: 'enrolled',
	IN_PROGRESS: 'in_progress',
	COMPLETED: 'completed',
	DROPPED: 'dropped'
};

export const QUIZ_TYPES = {
	PRACTICE: 'practice',
	GRADED: 'graded',
	FINAL: 'final',
	SURVEY: 'survey'
};

export const NOTIFICATION_TYPES = {
	ENROLLMENT: 'enrollment',
	COURSE_UPDATE: 'course_update',
	LESSON_AVAILABLE: 'lesson_available',
	ASSIGNMENT_DUE: 'assignment_due',
	QUIZ_RESULT: 'quiz_result',
	CERTIFICATE_READY: 'certificate_ready',
	FORUM_REPLY: 'forum_reply',
	ANNOUNCEMENT: 'announcement',
	SYSTEM: 'system'
};

export const BREAKPOINTS = {
	SM: 640,
	MD: 768,
	LG: 1024,
	XL: 1280,
	'2XL': 1536
};

// Modern color palette optimized for e-learning
export const COLORS = {
	primary: {
		50: '#f0f4ff',
		100: '#e0e7ff',
		200: '#c7d2fe',
		300: '#a5b4fc',
		400: '#818cf8',
		500: '#6366f1',
		600: '#4f46e5',
		700: '#4338ca',
		800: '#3730a3',
		900: '#312e81'
	},
	secondary: {
		50: '#fdf4ff',
		100: '#fae8ff',
		200: '#f5d0fe',
		300: '#f0abfc',
		400: '#e879f9',
		500: '#d946ef',
		600: '#c026d3',
		700: '#a21caf',
		800: '#86198f',
		900: '#701a75'
	},
	accent: {
		50: '#fefce8',
		100: '#fef9c3',
		200: '#fef08a',
		300: '#fde047',
		400: '#facc15',
		500: '#eab308',
		600: '#ca8a04',
		700: '#a16207',
		800: '#854d0e',
		900: '#713f12'
	}
};