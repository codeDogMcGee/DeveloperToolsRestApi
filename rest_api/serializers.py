from rest_framework import serializers


class LicenseListField(serializers.ListField):
    name = serializers.CharField(max_length=100, allow_blank=False)


class MostActiveMonthsListField(serializers.ListField):
    month = serializers.IntegerField()


class OrganizationsListField(serializers.ListField):
    organization = serializers.JSONField()


class ReleaseSerializer(serializers.Serializer):
    organization = serializers.CharField(max_length=100, allow_blank=False)
    release_count = serializers.IntegerField()
    total_labor_hours = serializers.IntegerField()
    all_in_production = serializers.BooleanField(required=True)
    licenses = LicenseListField()
    most_active_months = MostActiveMonthsListField()


class OrganizationsSerializer(serializers.Serializer):
    organizations = OrganizationsListField()

    
    
