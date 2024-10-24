from rest_framework import serializers

from users.models import Review
from business.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'company_name',
            'category',
            'subcategory',
            'first_name',
            'last_name',
            'job_title',
            'work_email',
            'phone_number',
            'country',
            'website',
            'created_at',
            'is_verified',
            'is_claimed',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'is_verified': {'read_only': True},
            'is_claimed': {'read_only': True},
        }

    def create(self, validated_data):
        if 'category' in validated_data:
            validated_data['category'] = validated_data['category'].lower().replace(' ', '_')
        if 'subcategory' in validated_data:
            validated_data['subcategory'] = validated_data['subcategory'].lower().replace(' ', '_')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            validated_data['category'] = validated_data['category'].lower().replace(' ', '_')
        if 'subcategory' in validated_data:
            validated_data['subcategory'] = validated_data['subcategory'].lower().replace(' ', '_')

        return super().update(instance, validated_data)

class CompanySummarySerializer(serializers.ModelSerializer):
    number_of_reviews = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField(source='avg_rating')

    class Meta:
        model = Company
        fields = [
            'id',
            'company_name',
            'category',
            'subcategory',
            'country',
            'website',
            'is_verified',
            'is_claimed',
            'number_of_reviews',
            'average_rating'
        ]

class CompanyReviewSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), many=False)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'company',
            'rating',
            'title',
            'review_body',
            'created_at',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'user_id': instance.user.id,
            'name': instance.user.name,
            'country': instance.user.country,
            'number_of_reviews': instance.user.number_of_reviews,
        }
        return representation
