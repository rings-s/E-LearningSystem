// front/src/lib/utils/validators.js
export const validators = {
	email(value) {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(value);
	},

	password(value) {
		return value && value.length >= 8;
	},

	phoneNumber(value) {
		const phoneRegex = /^\+?1?\d{9,15}$/;
		return !value || phoneRegex.test(value);
	},

	required(value) {
		return value !== null && value !== undefined && value !== '';
	},

	minLength(min) {
		return (value) => !value || value.length >= min;
	},

	maxLength(max) {
		return (value) => !value || value.length <= max;
	},

	pattern(regex) {
		return (value) => !value || regex.test(value);
	},

	matchField(fieldName) {
		return (value, allValues) => value === allValues[fieldName];
	}
};

// Form validation helper
export function validateForm(data, rules) {
	const errors = {};

	Object.keys(rules).forEach((field) => {
		const fieldRules = rules[field];
		const value = data[field];

		for (const rule of fieldRules) {
			let isValid = true;
			let message = '';

			if (typeof rule === 'function') {
				isValid = rule(value, data);
				message = 'Invalid value';
			} else if (typeof rule === 'object') {
				isValid = rule.validator(value, data);
				message = rule.message || 'Invalid value';
			}

			if (!isValid) {
				errors[field] = message;
				break;
			}
		}
	});

	return {
		isValid: Object.keys(errors).length === 0,
		errors
	};
}
