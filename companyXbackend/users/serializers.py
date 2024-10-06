from business.models import Company
from business.serializers import CompanySerializer

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, Review, ReviewFlags, ReviewLikes

# class RequestOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()


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
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            country=validated_data['country'],
            language=validated_data['language']
        )
        user.save()

        return user

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    company = CompanySerializer()

    class Meta:
        module = Review
        fields = [
            "user",
            "company",
            "rating",
            "title",
            "review_body",
            "date_of_experience",
            "invoice_number",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

        def create(self, validated_data):
            #TODO: check how this should work
            user = self.context['request'].user
            company_id = self.context['request'].data.get('company')
            company = Company.objects.get(id=company_id)
            return Review.objects.create(user=user, company=company, **validated_data)

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
