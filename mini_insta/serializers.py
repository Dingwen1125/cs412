from rest_framework import serializers

from .models import Follow, Photo, Post, Profile


def build_absolute_media_url(serializer, url):
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        return url

    request = serializer.context.get("request")
    if request is None:
        return url
    return request.build_absolute_uri(url)


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "image", "timestamp"]

    def get_image(self, obj):
        return build_absolute_media_url(self, obj.get_image_url())


class ProfileSummarySerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "username", "display_name", "profile_image"]

    def get_profile_image(self, obj):
        return build_absolute_media_url(self, obj.get_profile_image_url())


class ProfileSerializer(ProfileSummarySerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    profile_url = serializers.HyperlinkedIdentityField(
        view_name="api_profile_detail",
        lookup_field="pk",
    )

    class Meta(ProfileSummarySerializer.Meta):
        fields = ProfileSummarySerializer.Meta.fields + [
            "bio_text",
            "join_date",
            "follower_count",
            "following_count",
            "profile_url",
        ]

    def get_follower_count(self, obj):
        return obj.get_num_followers()

    def get_following_count(self, obj):
        return obj.get_num_following()


class PostSerializer(serializers.ModelSerializer):
    profile = ProfileSummarySerializer(read_only=True)
    photos = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "profile",
            "caption",
            "timestamp",
            "photos",
            "like_count",
            "comment_count",
        ]

    def get_photos(self, obj):
        photos = obj.get_all_photos()
        return PhotoSerializer(photos, many=True, context=self.context).data

    def get_like_count(self, obj):
        return obj.get_likes().count()

    def get_comment_count(self, obj):
        return obj.get_all_comments().count()


class CreatePostSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    image_files = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    photos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "caption", "timestamp", "image_urls", "image_files", "photos"]
        read_only_fields = ["id", "timestamp", "photos"]

    def validate(self, attrs):
        request = self.context["request"]
        if not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required to create a post.")

        if not Profile.objects.filter(user=request.user).exists():
            raise serializers.ValidationError("The authenticated user does not have a profile.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        profile = Profile.objects.filter(user=request.user).order_by("pk").first()
        image_urls = validated_data.pop("image_urls", [])
        image_files = validated_data.pop("image_files", [])

        post = Post.objects.create(profile=profile, **validated_data)

        for image_url in image_urls:
            Photo.objects.create(post=post, image_url=image_url)

        for image_file in image_files:
            Photo.objects.create(post=post, image_file=image_file)

        return post

    def get_photos(self, obj):
        return PhotoSerializer(obj.get_all_photos(), many=True, context=self.context).data
