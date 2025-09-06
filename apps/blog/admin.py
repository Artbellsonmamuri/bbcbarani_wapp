from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from .models import BlogPost, BlogCategory, Comment, BlogPostView, BlogSubscriber


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('get_author_name', 'content_preview', 'status', 'created_at')
    readonly_fields = ('get_author_name', 'content_preview', 'created_at')

    def get_author_name(self, obj):
        return obj.get_author_name()
    get_author_name.short_description = 'Author'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'icon', 'post_count', 'is_active', 'order')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Visual', {
            'fields': ('color', 'icon')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    def post_count(self, obj):
        return obj.blogpost_set.filter(status='published').count()
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'featured', 'comment_count', 'view_count', 'published_date')
    list_filter = ('status', 'category', 'featured', 'sticky', 'allow_comments', 'author', 'created_at')
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'comment_count', 'reading_time', 'created_at', 'updated_at')
    filter_horizontal = ('co_authors',)
    date_hierarchy = 'published_date'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Organization', {
            'fields': ('category', 'tags', 'author', 'co_authors')
        }),
        ('Publishing', {
            'fields': ('status', 'published_date', 'featured', 'sticky')
        }),
        ('Comments', {
            'fields': ('allow_comments', 'comments_require_approval')
        }),
        ('SEO & Social', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'comment_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [CommentInline]
    actions = ['make_published', 'make_featured', 'make_draft']

    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_date=timezone.now())
        messages.success(request, f'{updated} posts published.')
    make_published.short_description = 'Publish selected posts'

    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        messages.success(request, f'{updated} posts marked as featured.')
    make_featured.short_description = 'Mark as featured'

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        messages.success(request, f'{updated} posts moved to draft.')
    make_draft.short_description = 'Move to draft'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'get_author_name', 'content_preview', 'status', 'is_reply', 'created_at')
    list_filter = ('status', 'blog_post__category', 'user__isnull', 'created_at')
    search_fields = ('content', 'guest_name', 'guest_email', 'user__username', 'blog_post__title')
    readonly_fields = ('ip_address', 'user_agent', 'created_at', 'updated_at')

    fieldsets = (
        ('Comment Details', {
            'fields': ('blog_post', 'content', 'parent')
        }),
        ('Author Information', {
            'fields': ('user', 'guest_name', 'guest_email', 'guest_website')
        }),
        ('Moderation', {
            'fields': ('status', 'moderated_by', 'moderated_at')
        }),
        ('Technical', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_comments', 'reject_comments', 'mark_as_spam']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def get_author_name(self, obj):
        return obj.get_author_name()
    get_author_name.short_description = 'Author'

    def is_reply(self, obj):
        return bool(obj.parent)
    is_reply.boolean = True
    is_reply.short_description = 'Reply'

    def approve_comments(self, request, queryset):
        updated = queryset.update(status='approved', moderated_by=request.user, moderated_at=timezone.now())
        messages.success(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def reject_comments(self, request, queryset):
        updated = queryset.update(status='rejected', moderated_by=request.user, moderated_at=timezone.now())
        messages.success(request, f'{updated} comments rejected.')
    reject_comments.short_description = 'Reject selected comments'

    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='spam', moderated_by=request.user, moderated_at=timezone.now())
        messages.success(request, f'{updated} comments marked as spam.')
    mark_as_spam.short_description = 'Mark as spam'


@admin.register(BlogSubscriber)
class BlogSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'frequency', 'is_active', 'email_verified', 'subscribed_at')
    list_filter = ('frequency', 'is_active', 'email_verified', 'subscribed_at')
    search_fields = ('email', 'name')
    filter_horizontal = ('categories',)
    readonly_fields = ('verification_token', 'subscribed_at', 'last_email_sent')

    actions = ['verify_emails', 'send_test_email']

    def verify_emails(self, request, queryset):
        updated = queryset.update(email_verified=True)
        messages.success(request, f'{updated} email addresses verified.')
    verify_emails.short_description = 'Mark emails as verified'


@admin.register(BlogPostView)
class BlogPostViewAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'user', 'ip_address', 'viewed_at')
    list_filter = ('blog_post', 'viewed_at')
    search_fields = ('blog_post__title', 'user__username', 'ip_address')
    readonly_fields = ('blog_post', 'user', 'ip_address', 'user_agent', 'referer', 'viewed_at')

    def has_add_permission(self, request):
        return False  # Views are created automatically
