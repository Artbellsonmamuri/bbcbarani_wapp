from rest_framework import serializers
from .models import BlogPost, BlogCategory, Comment, BlogSubscriber


class BlogCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = '__all__'

    def get_post_count(self, obj):
        return obj.blogpost_set.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('user', 'ip_address', 'user_agent', 'moderated_by', 'moderated_at', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        return obj.get_author_name()

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.can_be_edited_by(request.user)
        return False

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(status='approved'), many=True, context=self.context).data
        return []

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_authenticated:
            validated_data['user'] = request.user

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            validated_data['ip_address'] = x_forwarded_for.split(',')[0]
        else:
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')

        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        return super().create(validated_data)


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    featured_image_url = serializers.CharField(source='featured_image.file.url', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ('author', 'view_count', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class BlogPostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for blog post lists"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    featured_image_url = serializers.CharField(source='featured_image.file.url', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'author_name',
            'category', 'category_name', 'featured_image_url', 'featured',
            'sticky', 'published_date', 'reading_time', 'comment_count', 'view_count'
        ]


class BlogSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSubscriber
        fields = '__all__'
        read_only_fields = ('verification_token', 'subscribed_at', 'last_email_sent')
