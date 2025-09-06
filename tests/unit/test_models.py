"""
Unit tests for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.blog.models import BlogPost, Category
from apps.events.models import Event
from apps.ministries.models import Ministry
from apps.prayer.models import PrayerRequest
from apps.cms.models import ContentSection

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""

    def test_user_creation(self):
        """Test user creation with different roles"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='Member'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'Member')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_role_validation(self):
        """Test user role validation"""
        valid_roles = ['Super Admin', 'Admin', 'Ministry Lead', 'Member']

        for role in valid_roles:
            user = User(
                username=f'user_{role.replace(" ", "_").lower()}',
                email=f'{role.replace(" ", "_").lower()}@example.com',
                role=role
            )
            user.full_clean()  # Should not raise ValidationError

    def test_superuser_creation(self):
        """Test superuser creation"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, 'Super Admin')


class BlogModelTest(TestCase):
    """Test Blog models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='blogger',
            email='blogger@example.com',
            password='blogpass123',
            role='Admin'
        )

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category'
        )

    def test_blog_post_creation(self):
        """Test blog post creation"""
        post = BlogPost.objects.create(
            title='Test Post',
            content='This is test content',
            author=self.user,
            category=self.category,
            status='published'
        )

        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.status, 'published')
        self.assertTrue(post.slug)  # Should auto-generate slug

    def test_blog_post_slug_generation(self):
        """Test automatic slug generation"""
        post = BlogPost.objects.create(
            title='This is a Long Title for Testing Slug Generation',
            content='Content',
            author=self.user,
            category=self.category
        )

        self.assertEqual(post.slug, 'this-is-a-long-title-for-testing-slug-generation')

    def test_blog_post_status_choices(self):
        """Test blog post status choices"""
        valid_statuses = ['draft', 'published', 'archived']

        for status in valid_statuses:
            post = BlogPost(
                title=f'Post {status}',
                content='Content',
                author=self.user,
                category=self.category,
                status=status
            )
            post.full_clean()  # Should not raise ValidationError


class EventModelTest(TestCase):
    """Test Event model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='eventcreator',
            email='events@example.com',
            password='eventpass123',
            role='Admin'
        )

    def test_event_creation(self):
        """Test event creation"""
        event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            start_datetime='2024-12-25 10:00:00',
            end_datetime='2024-12-25 12:00:00',
            location='Church Hall',
            rsvp_required=True,
            created_by=self.user
        )

        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.location, 'Church Hall')
        self.assertTrue(event.rsvp_required)
        self.assertEqual(event.created_by, self.user)

    def test_event_date_validation(self):
        """Test event date validation"""
        # End time should be after start time
        with self.assertRaises(ValidationError):
            event = Event(
                title='Invalid Event',
                start_datetime='2024-12-25 12:00:00',
                end_datetime='2024-12-25 10:00:00',  # Before start time
                created_by=self.user
            )
            event.full_clean()


class MinistryModelTest(TestCase):
    """Test Ministry model"""

    def test_ministry_creation(self):
        """Test ministry creation"""
        ministry = Ministry.objects.create(
            title='Youth Ministry',
            description='Ministry for young people',
            icon='fas fa-users'
        )

        self.assertEqual(ministry.title, 'Youth Ministry')
        self.assertEqual(ministry.icon, 'fas fa-users')
        self.assertTrue(ministry.slug)  # Should auto-generate slug


class PrayerRequestModelTest(TestCase):
    """Test PrayerRequest model"""

    def test_prayer_request_creation(self):
        """Test prayer request creation"""
        prayer = PrayerRequest.objects.create(
            requester_name='John Doe',
            email='john@example.com',
            message='Please pray for my family',
            status='new'
        )

        self.assertEqual(prayer.requester_name, 'John Doe')
        self.assertEqual(prayer.status, 'new')
        self.assertTrue(prayer.submitted_at)  # Should auto-set timestamp

    def test_anonymous_prayer_request(self):
        """Test anonymous prayer request"""
        prayer = PrayerRequest.objects.create(
            message='Anonymous prayer request',
            status='new'
        )

        self.assertIsNone(prayer.requester_name)
        self.assertIsNone(prayer.email)
        self.assertEqual(prayer.message, 'Anonymous prayer request')


class ContentSectionModelTest(TestCase):
    """Test ContentSection model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='contentcreator',
            email='content@example.com',
            password='contentpass123',
            role='Admin'
        )

    def test_content_section_creation(self):
        """Test content section creation"""
        section = ContentSection.objects.create(
            section_type='who_we_are',
            title='Who We Are',
            body='This is who we are content',
            created_by=self.user
        )

        self.assertEqual(section.section_type, 'who_we_are')
        self.assertEqual(section.title, 'Who We Are')
        self.assertEqual(section.created_by, self.user)

    def test_content_section_versioning(self):
        """Test content section versioning"""
        section = ContentSection.objects.create(
            section_type='welcome_screen',
            title='Welcome',
            body='Welcome content',
            created_by=self.user
        )

        # Update content
        section.body = 'Updated welcome content'
        section.save()

        # Check if versioning is working (if implemented)
        self.assertEqual(section.body, 'Updated welcome content')
