import os, random, uuid
from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator

def user_avatar_path(instance, filename):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    user_uuid = instance.uuid if instance.uuid else 'temp'
    return f'users/{user_uuid}/avatars/{timestamp}_{filename}'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_staff=True and is_superuser=True'))

        with transaction.atomic():
            return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', _('Student')),
        ('teacher', _('Teacher')),
        ('moderator', _('Moderator')),
        ('manager', _('Manager')),
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'), db_index=True)
    username = None
    email = models.EmailField(_('Email'), unique=True, db_index=True)
    first_name = models.CharField(_('First name'), max_length=150)
    last_name = models.CharField(_('Last name'), max_length=150)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be in format: '+999999999'. Max 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name=_('Phone number'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of birth'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_created = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name=_('Avatar'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name=_('User Role'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def has_role(self, role_name):
        return self.role == role_name or self.is_superuser

    def generate_verification_code(self, length=6):
        code = str(random.randint(10**(length-1), 10**length-1))
        self.verification_code = code
        self.verification_code_created = timezone.now()
        self.is_verified = False
        self.save(update_fields=['verification_code', 'verification_code_created', 'is_verified'])
        return code

    def verify_account(self, code):
        if not self.verification_code or not self.verification_code_created or self.verification_code != code:
            return False
        
        expiry_time = self.verification_code_created + timezone.timedelta(hours=24)
        if timezone.now() > expiry_time:
            return False

        self.is_verified = True
        self.verification_code = None
        self.verification_code_created = None
        self.save(update_fields=['is_verified', 'verification_code', 'verification_code_created'])
        return True

    def generate_reset_code(self, length=6):
        code = str(random.randint(10**(length-1), 10**length-1))
        self.reset_code = code
        self.reset_code_created = timezone.now()
        self.save(update_fields=['reset_code', 'reset_code_created'])
        return code

    def reset_password(self, code, new_password):
        if not self.reset_code or not self.reset_code_created or self.reset_code != code:
            return False
        
        expiry_time = self.reset_code_created + timezone.timedelta(hours=1)
        if timezone.now() > expiry_time:
            return False

        self.set_password(new_password)
        self.reset_code = None
        self.reset_code_created = None
        self.save(update_fields=['password', 'reset_code', 'reset_code_created'])
        return True

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
        if is_new:
            UserProfile.objects.get_or_create(user=self)

    # Dashboard methods for E-Learning
    def get_dashboard_priority(self):
        """Get user dashboard priority based on role"""
        priority_map = {
            'student': 1,
            'teacher': 3,
            'moderator': 2,
            'manager': 4,
        }
        base_priority = priority_map.get(self.role, 1)
        if self.is_superuser:
            base_priority = 5
        elif self.is_staff:
            base_priority += 1
        return base_priority

    def get_enrolled_courses(self):
        """Get courses enrolled by the user"""
        from courses.models import Enrollment
        if self.role == 'student':
            return Enrollment.objects.filter(student=self).select_related('course')
        return Enrollment.objects.none()

    def get_teaching_courses(self):
        """Get courses taught by the user"""
        from courses.models import Course
        if self.role == 'teacher':
            return Course.objects.filter(instructor=self)
        return Course.objects.none()

    def get_completion_rate(self):
        """Calculate overall course completion rate"""
        if self.role != 'student':
            return 0
        from courses.models import Enrollment
        enrollments = Enrollment.objects.filter(student=self)
        if not enrollments.exists():
            return 0
        completed = enrollments.filter(status='completed').count()
        return (completed / enrollments.count()) * 100


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    bio = models.TextField(blank=True, verbose_name=_('Biography'))
    
    # Educational Background
    education_level = models.CharField(max_length=50, blank=True, verbose_name=_('Education Level'))
    institution = models.CharField(max_length=200, blank=True, verbose_name=_('Institution'))
    field_of_study = models.CharField(max_length=200, blank=True, verbose_name=_('Field of Study'))
    
    # Teacher specific fields
    teaching_experience = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Years of Teaching Experience'))
    expertise_areas = models.TextField(blank=True, verbose_name=_('Areas of Expertise'))
    certifications = models.TextField(blank=True, verbose_name=_('Professional Certifications'))
    
    # Student preferences
    learning_goals = models.TextField(blank=True, verbose_name=_('Learning Goals'))
    preferred_language = models.CharField(max_length=10, default='en', verbose_name=_('Preferred Language'))
    time_zone = models.CharField(max_length=50, default='UTC', verbose_name=_('Time Zone'))
    
    # Address
    address = models.TextField(blank=True, verbose_name=_('Address'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, blank=True, verbose_name=_('State/Province'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('Postal Code'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    
    # Statistics
    courses_completed = models.PositiveIntegerField(default=0, verbose_name=_('Courses Completed'))
    total_study_hours = models.PositiveIntegerField(default=0, verbose_name=_('Total Study Hours'))
    points_earned = models.PositiveIntegerField(default=0, verbose_name=_('Points Earned'))
    
    # Social
    linkedin_url = models.URLField(blank=True, verbose_name=_('LinkedIn Profile'))
    github_url = models.URLField(blank=True, verbose_name=_('GitHub Profile'))
    website_url = models.URLField(blank=True, verbose_name=_('Personal Website'))

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"Profile for {self.user.email}"