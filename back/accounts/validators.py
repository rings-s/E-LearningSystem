# back/accounts/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Simple password validator for basic requirements
    """
    
    def validate(self, password, user=None):
        # Simple validation - just check minimum length
        if len(password) < 8:
            raise ValidationError(_('Password must be at least 8 characters long.'))
    
    def get_help_text(self):
        return _('Your password must be at least 8 characters long.')