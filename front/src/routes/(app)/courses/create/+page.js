import { redirect } from '@sveltejs/kit';

// Course creation lives in the teacher area
export function load() {
	redirect(307, '/teacher/courses/create');
}
