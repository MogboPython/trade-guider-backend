from rest_framework import serializers

from business.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
