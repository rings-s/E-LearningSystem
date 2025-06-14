import django_filters
from django.db.models import Q
from .models import Course, Lesson, Quiz, Certificate

class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__slug')
    level = django_filters.ChoiceFilter(choices=Course.LEVEL_CHOICES)
    language = django_filters.CharFilter()
    instructor = django_filters.CharFilter(field_name='instructor__uuid')
    min_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_hours', lookup_expr='lte')
    is_featured = django_filters.BooleanFilter()
    status = django_filters.ChoiceFilter(choices=Course.STATUS_CHOICES)
    tags = django_filters.CharFilter(method='filter_tags')
    search = django_filters.CharFilter(method='search_filter')
    
    class Meta:
        model = Course
        fields = ['title', 'category', 'level', 'language', 'instructor', 'is_featured', 'status']
    
    def filter_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__slug__in=tags).distinct()
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(instructor__first_name__icontains=value) |
            Q(instructor__last_name__icontains=value)
        ).distinct()

class LessonFilter(django_filters.FilterSet):
    module = django_filters.CharFilter(field_name='module__uuid')
    course = django_filters.CharFilter(field_name='module__course__uuid')
    content_type = django_filters.ChoiceFilter(choices=Lesson.CONTENT_TYPE_CHOICES)
    is_preview = django_filters.BooleanFilter()
    is_published = django_filters.BooleanFilter()
    
    class Meta:
        model = Lesson
        fields = ['module', 'course', 'content_type', 'is_preview', 'is_published']

class QuizFilter(django_filters.FilterSet):
    course = django_filters.CharFilter(field_name='course__uuid')
    quiz_type = django_filters.ChoiceFilter(choices=Quiz.QUIZ_TYPE_CHOICES)
    is_published = django_filters.BooleanFilter()
    
    class Meta:
        model = Quiz
        fields = ['course', 'quiz_type', 'is_published']