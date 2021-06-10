from django.views import View
from django.shortcuts import render
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .helpers import get_json_from_api, create_serialized_organizations_object, DATA_URL


class IndexView(View):
    template_name = 'rest_api/index.html'

    def get(self, request):
        return render(request, self.template_name)


class OrganizationsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        data_response = get_json_from_api(DATA_URL)
        data_from_source = data_response['data']

        if data_response['status'] == 200 and 'releases' in data_from_source.keys():
            
            organizations_json = create_serialized_organizations_object(data_from_source['releases'])

            if len(organizations_json) > 0:
                return Response(status=status.HTTP_200_OK, data=organizations_json)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationsSortedView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, sort_column='organization', ascending=1):
        if ascending > 1 or sort_column not in ['organization', 'release_count', 'total_labor_hours']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data_response = get_json_from_api(DATA_URL)
        data_from_source = data_response['data']

        if data_response['status'] == 200 and 'releases' in data_from_source.keys():
            
            organizations_json = create_serialized_organizations_object(data_from_source['releases'], sort_column, ascending)

            if len(organizations_json) > 0:
                return Response(status=status.HTTP_200_OK, data=organizations_json)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_204_NO_CONTENT)