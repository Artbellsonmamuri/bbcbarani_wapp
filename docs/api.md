# API Documentation

The Bible Baptist Church Barani CMS provides a comprehensive RESTful API for all content management and mobile integration needs.

## Base URL

- **Production**: `https://bbcbarani.org/api/`
- **Development**: `http://localhost:8000/api/`

## Authentication

### Token Authentication

The API uses Token-based authentication for secure access.

#### Obtain Token
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@bbcbarani.org",
        "role": "Super Admin"
    }
}
```

#### Use Token
Include the token in the Authorization header:
```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

#### Logout
```http
POST /api/auth/logout/
Authorization: Token your-token-here
```

### Session Authentication

Web-based applications can use session authentication through login forms.

## Content Management System (CMS)

### Content Sections

Manage sectional content for the website.

#### List Content Sections
```http
GET /api/cms/
Authorization: Token your-token-here
```

**Query Parameters:**
- `section_type`: Filter by section type (e.g., `welcome_screen`, `who_we_are`)
- `language`: Filter by language code (e.g., `en`, `es`)
- `page`: Page number for pagination
- `page_size`: Number of results per page (max 100)

**Response:**
```json
{
    "count": 15,
    "next": "https://bbcbarani.org/api/cms/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "section_type": "welcome_screen",
            "title": "Welcome to Our Church",
            "body": "<p>Welcome message content...</p>",
            "metadata": {
                "seo_title": "Welcome",
                "seo_description": "Welcome to Bible Baptist Church Barani"
            },
            "created_by": {
                "id": 1,
                "username": "admin"
            },
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T14:20:00Z"
        }
    ]
}
```

#### Get Content Section
```http
GET /api/cms/{id}/
Authorization: Token your-token-here
```

#### Create Content Section
```http
POST /api/cms/
Authorization: Token your-token-here
Content-Type: application/json

{
    "section_type": "who_we_are",
    "title": "About Our Church",
    "body": "<h2>Our Mission</h2><p>We are dedicated to...</p>",
    "metadata": {
        "seo_title": "About Us",
        "seo_description": "Learn about our church mission and values"
    }
}
```

#### Update Content Section
```http
PUT /api/cms/{id}/
Authorization: Token your-token-here
Content-Type: application/json

{
    "title": "Updated Title",
    "body": "<p>Updated content...</p>"
}
```

#### Delete Content Section
```http
DELETE /api/cms/{id}/
Authorization: Token your-token-here
```

## Blog Management

### Blog Posts

#### List Blog Posts
```http
GET /api/blog/
```

**Query Parameters:**
- `status`: Filter by status (`published`, `draft`, `archived`)
- `category`: Filter by category ID
- `author`: Filter by author ID
- `search`: Search in title and content
- `ordering`: Order by field (`-created_at`, `title`, etc.)

**Response:**
```json
{
    "count": 25,
    "next": "https://bbcbarani.org/api/blog/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Sunday Service Highlights",
            "slug": "sunday-service-highlights",
            "content": "<p>Today's service was wonderful...</p>",
            "excerpt": "Today's service was wonderful...",
            "featured_image": "https://bbcbarani.org/media/blog/featured.jpg",
            "status": "published",
            "category": {
                "id": 1,
                "name": "Sermons",
                "slug": "sermons"
            },
            "author": {
                "id": 1,
                "username": "pastor",
                "full_name": "Pastor John Smith"
            },
            "tags": ["sermon", "sunday", "worship"],
            "comment_count": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T14:20:00Z"
        }
    ]
}
```

#### Get Blog Post
```http
GET /api/blog/{id}/
```

#### Create Blog Post
```http
POST /api/blog/
Authorization: Token your-token-here
Content-Type: application/json

{
    "title": "New Blog Post",
    "content": "<p>Blog post content here...</p>",
    "excerpt": "Short excerpt...",
    "category": 1,
    "tags": ["tag1", "tag2"],
    "status": "published"
}
```

#### Update Blog Post
```http
PUT /api/blog/{id}/
Authorization: Token your-token-here
Content-Type: application/json

{
    "title": "Updated Blog Post Title",
    "content": "<p>Updated content...</p>"
}
```

#### Delete Blog Post
```http
DELETE /api/blog/{id}/
Authorization: Token your-token-here
```

### Categories

#### List Categories
```http
GET /api/blog/categories/
```

#### Create Category
```http
POST /api/blog/categories/
Authorization: Token your-token-here
Content-Type: application/json

{
    "name": "Youth Ministry",
    "description": "Posts about youth ministry activities"
}
```

### Comments

#### List Comments
```http
GET /api/blog/comments/
Authorization: Token your-token-here
```

**Query Parameters:**
- `post`: Filter by blog post ID
- `status`: Filter by status (`pending`, `approved`, `rejected`)

#### Moderate Comment
```http
PUT /api/blog/comments/{id}/
Authorization: Token your-token-here
Content-Type: application/json

{
    "status": "approved"
}
```

## Events Management

### Events

#### List Events
```http
GET /api/events/
```

**Query Parameters:**
- `start_date`: Filter events after date (YYYY-MM-DD)
- `end_date`: Filter events before date (YYYY-MM-DD)
- `rsvp_required`: Filter by RSVP requirement (true/false)

**Response:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Christmas Service",
            "description": "Join us for our special Christmas service...",
            "start_datetime": "2024-12-25T10:00:00Z",
            "end_datetime": "2024-12-25T12:00:00Z",
            "location": "Main Sanctuary",
            "featured_image": "https://bbcbarani.org/media/events/christmas.jpg",
            "rsvp_required": true,
            "rsvp_count": 125,
            "max_attendees": 200,
            "created_by": {
                "id": 1,
                "username": "admin"
            },
            "created_at": "2024-11-01T10:00:00Z"
        }
    ]
}
```

#### Get Event
```http
GET /api/events/{id}/
```

#### Create Event
```http
POST /api/events/
Authorization: Token your-token-here
Content-Type: application/json

{
    "title": "Bible Study",
    "description": "Weekly Bible study session",
    "start_datetime": "2024-01-20T19:00:00Z",
    "end_datetime": "2024-01-20T21:00:00Z",
    "location": "Fellowship Hall",
    "rsvp_required": false
}
```

#### RSVP to Event
```http
POST /api/events/{id}/rsvp/
Authorization: Token your-token-here
Content-Type: application/json

{
    "attending": true,
    "guest_count": 2,
    "notes": "Looking forward to it!"
}
```

## Ministries

### List Ministries
```http
GET /api/ministries/
```

**Response:**
```json
{
    "count": 8,
    "results": [
        {
            "id": 1,
            "title": "Youth Ministry",
            "slug": "youth-ministry",
            "description": "Ministry for teenagers and young adults...",
            "icon": "fas fa-users",
            "featured_image": "https://bbcbarani.org/media/ministries/youth.jpg",
            "carousel_images": [
                "https://bbcbarani.org/media/ministries/youth1.jpg",
                "https://bbcbarani.org/media/ministries/youth2.jpg"
            ],
            "leader": {
                "id": 3,
                "name": "John Doe",
                "email": "john@bbcbarani.org"
            },
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Ministry
```http
GET /api/ministries/{id}/
```

#### Create Ministry
```http
POST /api/ministries/
Authorization: Token your-token-here
Content-Type: application/json

{
    "title": "Music Ministry",
    "description": "Leading worship through music...",
    "icon": "fas fa-music"
}
```

## Prayer Requests

### Submit Prayer Request (Public)
```http
POST /api/prayer/
Content-Type: application/json

{
    "requester_name": "John Smith",
    "email": "john@example.com",
    "message": "Please pray for my family during this difficult time.",
    "is_anonymous": false
}
```

**Response:**
```json
{
    "id": 123,
    "message": "Thank you for your prayer request. Our pastoral team will be praying for you.",
    "submitted_at": "2024-01-15T15:30:00Z"
}
```

### List Prayer Requests (Admin Only)
```http
GET /api/prayer/
Authorization: Token your-token-here
```

**Query Parameters:**
- `status`: Filter by status (`new`, `reviewed`, `completed`)
- `is_anonymous`: Filter anonymous requests (true/false)

**Response:**
```json
{
    "count": 45,
    "results": [
        {
            "id": 123,
            "requester_name": "John Smith",
            "email": "john@example.com",
            "message": "Please pray for my family...",
            "status": "new",
            "is_anonymous": false,
            "submitted_at": "2024-01-15T15:30:00Z",
            "reviewed_by": null,
            "reviewed_at": null
        }
    ]
}
```

### Update Prayer Request Status
```http
PUT /api/prayer/{id}/
Authorization: Token your-token-here
Content-Type: application/json

{
    "status": "reviewed",
    "notes": "Contacted family, continuing to pray."
}
```

## Media Management

### List Media Files
```http
GET /api/media/
Authorization: Token your-token-here
```

**Query Parameters:**
- `media_type`: Filter by type (`image`, `video`, `document`)
- `tags`: Filter by tags (comma-separated)

**Response:**
```json
{
    "count": 150,
    "results": [
        {
            "id": 1,
            "file": "https://bbcbarani.org/media/uploads/church-photo.jpg",
            "file_name": "church-photo.jpg",
            "media_type": "image",
            "file_size": 245760,
            "alt_text": "Church building exterior",
            "tags": ["church", "building", "exterior"],
            "uploaded_by": {
                "id": 1,
                "username": "admin"
            },
            "created_at": "2024-01-10T12:00:00Z"
        }
    ]
}
```

### Upload Media File
```http
POST /api/media/
Authorization: Token your-token-here
Content-Type: multipart/form-data

file: [binary data]
alt_text: "Image description"
tags: "tag1,tag2,tag3"
```

### Delete Media File
```http
DELETE /api/media/{id}/
Authorization: Token your-token-here
```

## Notifications

### Get Notifications
```http
GET /api/notifications/
Authorization: Token your-token-here
```

**Response:**
```json
{
    "count": 3,
    "unread_count": 2,
    "results": [
        {
            "id": 1,
            "title": "New Prayer Request",
            "message": "A new prayer request has been submitted",
            "type": "prayer_request",
            "is_read": false,
            "created_at": "2024-01-15T16:00:00Z",
            "link": "/prayer/123/"
        }
    ]
}
```

### Get Notification Count
```http
GET /api/notifications/count/
Authorization: Token your-token-here
```

**Response:**
```json
{
    "count": 5,
    "unread_count": 3
}
```

### Mark Notification as Read
```http
POST /api/notifications/{id}/mark-read/
Authorization: Token your-token-here
```

### Mark All Notifications as Read
```http
POST /api/notifications/mark-all-read/
Authorization: Token your-token-here
```

## Analytics

### Track Page View
```http
POST /api/analytics/track-page-view/
Content-Type: application/json

{
    "url": "https://bbcbarani.org/",
    "path": "/",
    "title": "Home - Bible Baptist Church Barani",
    "referrer": "https://google.com",
    "user_agent": "Mozilla/5.0...",
    "session_id": "session_12345"
}
```

### Track Event
```http
POST /api/analytics/track-event/
Content-Type: application/json

{
    "event_name": "button_click",
    "event_data": {
        "button_text": "Contact Us",
        "page_url": "https://bbcbarani.org/"
    },
    "session_id": "session_12345"
}
```

### Get Analytics Data (Admin Only)
```http
GET /api/analytics/dashboard/
Authorization: Token your-token-here
```

**Response:**
```json
{
    "page_views": {
        "today": 125,
        "this_week": 890,
        "this_month": 3420
    },
    "popular_pages": [
        {
            "path": "/",
            "views": 1250,
            "title": "Home"
        },
        {
            "path": "/blog/",
            "views": 680,
            "title": "Blog"
        }
    ],
    "recent_events": [
        {
            "event_name": "form_submit",
            "count": 15,
            "date": "2024-01-15"
        }
    ]
}
```

## Themes

### List Themes
```http
GET /api/themes/
Authorization: Token your-token-here
```

**Response:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "name": "Default Theme",
            "is_active": true,
            "css_settings": {
                "primary_color": "#1e3a8a",
                "secondary_color": "#dc2626",
                "font_family": "Open Sans"
            },
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### Activate Theme
```http
PUT /api/themes/{id}/activate/
Authorization: Token your-token-here
```

### Update Theme Settings
```http
PUT /api/themes/{id}/
Authorization: Token your-token-here
Content-Type: application/json

{
    "css_settings": {
        "primary_color": "#2563eb",
        "secondary_color": "#ef4444"
    }
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": "error_code",
    "message": "Human-readable error message",
    "details": {
        "field_name": ["Field-specific error message"]
    }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour
- **Prayer requests**: 5 submissions per hour per IP

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

Pagination response format:
```json
{
    "count": 150,
    "next": "https://bbcbarani.org/api/endpoint/?page=2",
    "previous": null,
    "results": [...]
}
```

## Filtering and Search

Many endpoints support filtering and search:

### Common Filters
- `search`: Full-text search in relevant fields
- `ordering`: Sort by field (prefix with `-` for descending)
- Date filters: `created_after`, `created_before`

### Example
```http
GET /api/blog/?search=christmas&ordering=-created_at&category=1
```

## Webhooks

Configure webhooks to receive real-time notifications:

### Available Events
- `prayer_request.created`: New prayer request submitted
- `blog_post.published`: New blog post published
- `event.created`: New event created
- `comment.pending`: New comment awaiting moderation

### Webhook Configuration
```http
POST /api/webhooks/
Authorization: Token your-token-here
Content-Type: application/json

{
    "url": "https://your-app.com/webhook/",
    "events": ["prayer_request.created", "blog_post.published"],
    "secret": "your-webhook-secret"
}
```

## Mobile App Integration

### Example Mobile App Flow

1. **User Authentication**
   ```javascript
   const response = await fetch('/api/auth/login/', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({username, password})
   });
   const {token} = await response.json();
   ```

2. **Fetch Content**
   ```javascript
   const response = await fetch('/api/cms/?section_type=welcome_screen', {
       headers: {'Authorization': `Token ${token}`}
   });
   const content = await response.json();
   ```

3. **Submit Prayer Request**
   ```javascript
   const response = await fetch('/api/prayer/', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({message: prayerText})
   });
   ```

## SDKs and Libraries

### JavaScript SDK Example
```javascript
class BBCBaraniAPI {
    constructor(baseURL, token = null) {
        this.baseURL = baseURL;
        this.token = token;
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers
        });

        return response.json();
    }

    // Blog methods
    async getBlogPosts(params = {}) {
        const query = new URLSearchParams(params);
        return this.request(`/blog/?${query}`);
    }

    async createBlogPost(data) {
        return this.request('/blog/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Prayer request methods
    async submitPrayerRequest(data) {
        return this.request('/prayer/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// Usage
const api = new BBCBaraniAPI('https://bbcbarani.org/api');
const posts = await api.getBlogPosts({status: 'published'});
```

This API documentation provides comprehensive coverage of all available endpoints for the Bible Baptist Church Barani CMS. For additional help or custom integrations, contact the development team at admin@bbcbarani.org.
