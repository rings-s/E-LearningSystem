// Proposed Final Structure for the routes
(auth)/
├── login/
├── register/  
├── forgot-password/
├── reset-password/
└── verify-email/

(app)/
├── dashboard/                    # Role-based dashboard
├── courses/                      # Public catalog
│   ├── [uuid]/                  # Course details
│   │   ├── learn/              # Student learning
│   │   └── preview/            # Public preview
│   └── create/                 # Course creation
├── my-courses/                  # Student view
│   └── [uuid]/
│       ├── learn/              # Learning interface  
│       └── notes/              # Student notes
├── teacher/                     # Teacher hub
│   ├── dashboard/              # Teacher overview
│   ├── courses/                # My teaching courses
│   │   ├── [uuid]/
│   │   │   ├── manage/         # Course management
│   │   │   ├── analytics/      # Course analytics
│   │   │   └── lessons/
│   │   │       └── create/     # Lesson creation
│   │   └── create/             # New course creation
│   └── students/               # Student management
├── certificates/
├── forum/
└── profile/