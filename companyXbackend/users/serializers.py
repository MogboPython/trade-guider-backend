from business.models import Company

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, Review, ReviewFlags, ReviewLikes


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'country',
            'language',
            'created_at',
            'is_verified',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'is_verified': {'read_only': True},
        }

    def create(self, validated_data):
        return User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            country=validated_data['country'],
            language=validated_data['language']
        )

class ReviewSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), many = False)

    class Meta:
        model = Review
        fields = [
            'id',
            "user",
            "company",
            "rating",
            "title",
            "review_body",
            "date_of_experience",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        company = validated_data.pop('company')
        return Review.objects.create(
            user=user,
            company=company,
            rating=validated_data["rating"],
            title=validated_data["title"],
            review_body=validated_data["review_body"],
            date_of_experience=validated_data["date_of_experience"],

        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'user_id': instance.user.id,
            'name': instance.user.name,
            'country': instance.user.country,
            'number_of_reviews': instance.user.number_of_reviews,
        }
        representation['company'] = {
            'company_name': instance.company.company_name,
        }
        return representation

class ReviewLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLikes
        fields = ['id', 'user', 'review', 'created']
        read_only_fields = ['created_at']

class ReviewFlagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFlags
        fields = ['id', 'user', 'review', 'created']
        read_only_fields = ['created_at']

class ReviewDetailSerializer(ReviewSerializer):
    likes = ReviewLikesSerializer(many=True, read_only=True)
    flags = ReviewFlagsSerializer(many=True, read_only=True)

    class Meta(ReviewSerializer.Meta):
        fields = [*ReviewSerializer.Meta.fields, 'likes', 'flags']
