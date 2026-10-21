import { redirect } from '@sveltejs/kit';

// Course analytics live in the teacher area
export function load({ params }) {
	redirect(307, `/teacher/courses/${params.uuid}/analytics`);
}
