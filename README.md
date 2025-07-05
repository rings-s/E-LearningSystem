# 🎓 E-Learning Platform Backend API

A comprehensive Django REST Framework backend for a modern e-learning platform with role-based access, analytics, and real-time features.

## 📋 Table of Contents
- [Features Overview](#-features-overview)
- [System Architecture](#-system-architecture)
- [API Endpoints](#-api-endpoints)
- [Code Learning Guide](#-code-learning-guide)
- [Installation & Setup](#-installation--setup)
- [Database Models](#-database-models)
- [Authentication & Permissions](#-authentication--permissions)
- [Analytics System](#-analytics-system)

## 🚀 Features Overview

### 👥 **User Management System**
- **Multi-Role Authentication**: Student, Teacher, Manager, Admin roles
- **Email Verification**: Secure account verification with time-limited codes
- **Password Reset**: Secure password reset via email codes
- **User Profiles**: Extended profiles with educational background, preferences
- **Avatar Upload**: Profile image management
- **Activity Tracking**: Comprehensive user activity logging

### 📚 **Course Management**
- **Course Creation**: Rich course content with modules and lessons
- **Multiple Content Types**: Video, text, PDF, slides, interactive content
- **Course Categories & Tags**: Organized content structure
- **Prerequisites System**: Course dependency management
- **Enrollment Management**: Student enrollment with progress tracking
- **Course Reviews & Ratings**: Student feedback system
- **Draft/Published States**: Course lifecycle management

### 🎯 **Learning Experience**
- **Progress Tracking**: Detailed lesson and course completion tracking
- **Quiz System**: Multiple question types with automated scoring
- **Assignments**: File submissions and grading
- **Certificates**: Automated certificate generation upon completion
- **Learning Analytics**: Personal progress dashboards
- **Study Streaks**: Gamification elements

### 💬 **Discussion Forums**
- **Course Forums**: Dedicated discussion spaces per course
- **Question & Answer**: Q&A system with solution marking
- **Real-time Chat**: WebSocket-powered live discussions
- **Moderation Tools**: Pin, lock, resolve discussions
- **Threaded Replies**: Nested conversation support

### 📊 **Analytics Dashboard**
- **Student Analytics**: Progress, performance, study time tracking
- **Teacher Analytics**: Course performance, student engagement
- **Platform Analytics**: User growth, course distribution, platform health
- **Visual Charts**: Chart.js compatible data for beautiful dashboards
- **Performance Metrics**: Detailed KPIs for all stakeholders

### 🔔 **Notification System**
- **Real-time Notifications**: WebSocket-powered instant notifications
- **Email Notifications**: Automated email alerts
- **Notification Types**: Enrollment, assignments, announcements
- **Notification Center**: Unified notification management

### 🎫 **Support System**
- **Ticket Management**: Help desk ticket system
- **Priority Levels**: Urgent, high, medium, low priority support
- **Assignment System**: Ticket routing to support staff
- **Status Tracking**: Open, in progress, resolved, closed states

### 📁 **Media Management**
- **File Uploads**: Secure file upload with validation
- **Media Library**: Centralized media content management
- **Content Types**: Support for various file formats
- **Usage Tracking**: Media usage analytics

## 🏗️ System Architecture

### **Backend Framework**
- **Django 5.2**: Latest Django framework with enhanced features
- **Django REST Framework**: Powerful API development
- **PostgreSQL**: Robust relational database
- **Redis**: Caching and session management
- **Celery**: Background task processing
- **WebSockets**: Real-time communication

### **Key Design Patterns**
- **Repository Pattern**: Clean data access layer
- **Service Layer**: Business logic separation
- **Permission System**: Role-based access control
- **Serializer Pattern**: Data validation and transformation
- **UUID Primary Keys**: Secure, non-sequential identifiers

## 🔗 API Endpoints

### **Authentication**
```
POST /api/accounts/register/          # User registration
POST /api/accounts/login/             # User login
POST /api/accounts/verify-email/      # Email verification
POST /api/accounts/password-reset/    # Password reset request
GET  /api/accounts/users/me/          # Current user profile
```

### **Courses**
```
GET    /api/courses/courses/                    # List courses
POST   /api/courses/courses/                    # Create course
GET    /api/courses/courses/{uuid}/             # Course details
POST   /api/courses/courses/{uuid}/enroll/     # Enroll in course
GET    /api/courses/courses/{uuid}/lessons/    # Course lessons
POST   /api/courses/courses/{uuid}/lessons/    # Create lesson
```

### **Analytics**
```
GET /api/core/analytics/student/    # Student dashboard
GET /api/core/analytics/teacher/    # Teacher dashboard  
GET /api/core/analytics/platform/  # Platform analytics
GET /api/core/dashboard/            # Role-based dashboard
```

### **Forums**
```
GET    /api/core/discussions/              # List discussions
POST   /api/core/discussions/              # Create discussion
GET    /api/core/discussions/{uuid}/       # Discussion details
POST   /api/core/replies/                  # Create reply
POST   /api/core/replies/{uuid}/upvote/    # Upvote reply
```

## 📖 Code Learning Guide

### **1. Django Project Structure**
```
back/
├── accounts/          # User management app
├── courses/           # Course management app  
├── core/              # Core functionality (forums, analytics)
├── back/              # Project settings
└── manage.py          # Django management script
```

**Learning Points:**
- **App-based Architecture**: Django apps provide modularity
- **Separation of Concerns**: Each app handles specific functionality
- **Reusable Components**: Apps can be reused across projects

### **2. Model Design Patterns**

```python
class Course(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT)
    # ...
```

**Learning Points:**
- **UUID Primary Keys**: More secure than sequential IDs
- **Foreign Key Relationships**: Proper relational database design
- **Model Methods**: Business logic in model methods
- **Meta Classes**: Database optimization (indexes, ordering)

### **3. Serializer Patterns**

```python
class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user).exists()
        return False
```

**Learning Points:**
- **Data Transformation**: Convert complex data to JSON
- **Context Usage**: Access request data in serializers
- **Computed Fields**: Dynamic fields based on user context
- **Nested Serialization**: Handle related objects

### **4. Permission System**

```python
class IsCourseInstructor(BasePermission):
    def has_object_permission(self, request, view, obj):
        course = obj if hasattr(obj, 'instructor') else getattr(obj, 'course', None)
        return course.instructor == request.user or request.user.is_staff
```

**Learning Points:**
- **Custom Permissions**: Fine-grained access control
- **Object-level Permissions**: Per-object access rules
- **Role-based Access**: Different permissions for different roles
- **Security Best Practices**: Always verify user permissions

### **5. API View Patterns**

```python
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    lookup_field = 'uuid'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        increment_view_count(instance)  # Track views
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
```

**Learning Points:**
- **Generic Views**: DRF's powerful generic view classes
- **Method Overriding**: Customize behavior when needed
- **Middleware Pattern**: Add functionality without changing core logic
- **Response Formatting**: Consistent API responses

### **6. Database Optimization**

```python
def get_queryset(self):
    return super().get_queryset().select_related(
        'instructor', 'category'
    ).prefetch_related(
        'tags', 'co_instructors'
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        enrolled_count=Count('enrollments')
    )
```

**Learning Points:**
- **Query Optimization**: Reduce database hits
- **Select Related**: Efficient foreign key queries
- **Prefetch Related**: Efficient many-to-many queries
- **Annotations**: Database-level calculations

### **7. Error Handling**

```python
def validate_and_get_object(model_class, uuid_value):
    try:
        uuid.UUID(str(uuid_value))
        return get_object_or_404(model_class, uuid=uuid_value)
    except (ValueError, AttributeError, TypeError):
        raise Http404("Invalid UUID format")
```

**Learning Points:**
- **Input Validation**: Always validate user input
- **Custom Exceptions**: Meaningful error messages
- **Error Responses**: Consistent error handling
- **Security**: Prevent malicious input

### **8. Analytics Implementation**

```python
class StudentAnalyticsView(APIView):
    def get(self, request):
        # Calculate learning metrics
        enrollments = Enrollment.objects.filter(student=request.user)
        
        # Generate chart data
        charts = {
            'course_progress': {
                'type': 'bar',
                'data': {
                    'labels': [course.title for course in courses],
                    'datasets': [{'data': progress_data}]
                }
            }
        }
        return Response({'charts': charts})
```

**Learning Points:**
- **Data Aggregation**: Combine data from multiple sources
- **Chart Generation**: Structure data for frontend charts
- **Performance Metrics**: Calculate meaningful KPIs
- **Real-time Analytics**: Live dashboard updates

### **9. Real-time Features**

```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_group = f"user_{self.user.uuid}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
```

**Learning Points:**
- **WebSocket Implementation**: Real-time communication
- **Channel Layers**: Message routing
- **Async Programming**: Non-blocking operations
- **Group Management**: Targeted message delivery

### **10. Testing Patterns**

```python
class CourseAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com')
        self.course = Course.objects.create(title='Test Course', instructor=self.user)
    
    def test_course_enrollment(self):
        response = self.client.post(f'/api/courses/{self.course.uuid}/enroll/')
        self.assertEqual(response.status_code, 201)
```

**Learning Points:**
- **Test Setup**: Prepare test data
- **API Testing**: Test endpoints thoroughly
- **Test Coverage**: Ensure all features are tested
- **Mock Objects**: Isolate components during testing

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)

### **Backend Setup**
```bash
# Clone repository
git clone <repository-url>
cd e-learning-platform/back

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your database and email settings

# Database setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### **Environment Variables**
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

## 🗄️ Database Models

### **Core Models**
- **User**: Extended user model with roles and profiles
- **Course**: Course information with instructor and content
- **Enrollment**: Student-course relationship with progress
- **Module**: Course sections for organized content
- **Lesson**: Individual learning units with various content types

### **Assessment Models**
- **Quiz**: Assessment containers with settings
- **Question**: Individual quiz questions with types
- **Answer**: Question options with correctness flags
- **QuizAttempt**: Student quiz submissions with scores

### **Communication Models**
- **Forum**: Course discussion spaces
- **Discussion**: Individual discussion threads
- **Reply**: Threaded responses to discussions
- **Notification**: System notifications for users

## 🔐 Authentication & Permissions

### **Role Hierarchy**
1. **Student**: Enroll in courses, take quizzes, participate in discussions
2. **Teacher**: Create courses, manage content, view analytics
3. **Manager**: Platform management, user oversight
4. **Admin**: Full system access

### **Permission Classes**
- `IsOwnerOrReadOnly`: Object owners can edit
- `IsCourseInstructor`: Course instructors have access
- `IsEnrolledStudent`: Only enrolled students can access
- `IsModeratorOrUp`: Moderator-level permissions
- `IsVerifiedUser`: Email-verified users only

## 📊 Analytics System

### **Student Analytics**
- Course progress tracking
- Quiz performance trends
- Study time analysis
- Learning streak calculation
- Subject performance breakdown

### **Teacher Analytics**
- Course enrollment metrics
- Student engagement scores
- Discussion activity analysis
- Completion rate tracking
- Performance comparisons

### **Platform Analytics**
- User growth trends
- Course category distribution
- Platform health metrics
- Revenue analytics (if applicable)
- System usage statistics

## 🔧 Advanced Features

### **Background Tasks**
- Certificate generation
- Email notifications
- Data cleanup
- Report generation

### **Caching Strategy**
- Redis for session management
- Query result caching
- Media file caching
- API response caching

### **Security Features**
- Rate limiting
- Input validation
- SQL injection protection
- XSS prevention
- CSRF protection

## 📚 Learning Resources

### **Key Concepts to Master**
1. **Django ORM**: Database queries and relationships
2. **REST API Design**: RESTful endpoint creation
3. **Authentication**: Token-based auth with JWT
4. **Permissions**: Role-based access control
5. **Serialization**: Data transformation for APIs
6. **Testing**: Comprehensive test coverage
7. **Deployment**: Production-ready configurations

### **Next Steps for Learning**
1. Study the model relationships in `models.py` files
2. Understand serializer patterns in `serializers.py` files
3. Analyze view logic in `views.py` files
4. Explore permission classes in `permissions.py` files
5. Learn URL routing in `urls.py` files
6. Master testing patterns in `tests.py` files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django REST Framework for modern e-learning experiences**