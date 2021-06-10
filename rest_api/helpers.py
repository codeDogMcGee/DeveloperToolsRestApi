import json
import requests
import csv
from datetime import datetime
from collections import Counter, OrderedDict
from django.http.response import HttpResponse

from .serializers import ReleaseSerializer, OrganizationsSerializer

API_MAIN_ROUTE = 'http://127.0.0.1:8080/'

DATA_URL = 'https://www.energy.gov/sites/prod/files/2020/12/f81/code-12-15-2020.json'


def get_json_from_api(request_url: str) -> dict[str, object]:
    response = {}
    try:
        if len(request_url) > 0:
            response = requests.get(request_url)
    except Exception as e:
        raise e

    if response == {}:
        output = {'status': 404, 'content': {}}
    else:    
        response_code = response.status_code
        response_content = response.content.decode('utf-8')  # first convert the data from bytes to text
        response_content = json.loads(response_content)  # then convert the text to json
        output = {'status': response_code, 'data': response_content}
    return output



def csv_response(data):
    response = HttpResponse(content_type='text/csv',headers = {'Content-Disposition': 'attachment; filename="organizations.csv"'})
    writer = csv.DictWriter(response, fieldnames=['organization', 'release_count', 'total_labor_hours', 'all_in_production', 'licenses', 'most_active_months'])
    writer.writeheader()
    for row in data:
        writer.writerow(dict(row))
    return response


def create_serialized_organizations_object(releases_list: list[object], sort_column: str = 'organization', ascending: bool = True) -> json:
    descending = False if ascending else True
    releases_object = _make_object_from_releases(releases_list=releases_list, sort_by=sort_column, descending=descending)

    organizations_list = []
    for release_dict in releases_object.values():
        release_dict = _serialize_release(release_dict)
        organizations_list.append(release_dict)

    return _serialize_organizations(organizations_list)


def _serialize_release(releases_object: dict[str, object]) -> json:
    output = {}
    release_serializer = ReleaseSerializer(data=releases_object)
    if release_serializer.is_valid():
        output = release_serializer.validated_data
    else:
        output = {}
    return output


def _serialize_organizations(organizations: list[object]) -> json:
    organizations_object = {'organizations': organizations}
    organization_serializer = OrganizationsSerializer(data=organizations_object)
    if organization_serializer.is_valid():
        output = organization_serializer.validated_data
    else:
        output = {}
    return output


def _make_object_from_releases(releases_list: list[object], sort_by: str, descending: bool) -> OrderedDict[str, object]:
    """
    Iterate the releases and return an object with aggragated data.
    Output could be a list here but a dictionary lets us lookup thevalues to update faster than iterating the list each time.
    """

    output = OrderedDict()

    for release in releases_list:
        organization = release['organization']
        if release['organization'] in output.keys():           
            output[organization]['release_count'] += 1
            output[organization]['total_labor_hours'] += release['laborHours']
            output[organization]['all_in_production'] = _all_in_production(output[organization]['all_in_production'], release['status'])
            output[organization]['licenses'] = _unique_license_names(output[organization]['licenses'], release['permissions']['licenses'])
            output[organization]['most_active_months'].append(_datetime_string_to_month(release['date']['created']))
        else:
            # initialize new organization object
            new_object = {
                'organization': organization,
                'release_count': 1,
                'total_labor_hours': release['laborHours'],
                'all_in_production': _all_in_production(True, release['status']), # default to true because many scenarios can turn it off
                'licenses': _unique_license_names([], release['permissions']['licenses']),
                'most_active_months': [_datetime_string_to_month(release['date']['created'])]  # convert string to month int, and store in list to be tallied later
            }

            output[organization] = new_object

    # Here 'most_active_months' for each organization is a list of months, so we need to figure out which months have the most occurances,
    # while we're iterating convert total_labor_hours to an int,
    for organization in output.keys():
        output[organization]['most_active_months'] = _get_most_frequent_months(output[organization]['most_active_months'])

        output[organization]['total_labor_hours'] = int(output[organization]['total_labor_hours'])

    output = OrderedDict(sorted(output.items(), key=lambda x: x[1][sort_by], reverse=descending))
    return output


def _all_in_production(current_value: bool, release_status: str) -> bool:
    """
    Once set to false it can never be true again for that organization
    """
    if current_value is False:
        return False
    else:
        return True if release_status == 'Production' else False  # only return True if status is in Production


def _unique_license_names(current_license_list: list[str], new_license_list: list[object]) -> list[str]:
    output = current_license_list
    for license in new_license_list:
        if license['name'] not in output:
            output.append(license['name'])
    return output


def _datetime_string_to_month(date_string: str) -> int:
    return datetime.strptime(date_string, '%Y-%m-%d').month


def _get_most_frequent_months(input_list: list[int]) -> list[int]:
    """
    Given a list of months, return a list of the months that
    occur the most in the list. If there is a tie multiple months 
    will be returned
    """
    month_list = []
    if input_list and len(input_list) > 0:
        most_common = Counter(input_list).most_common()
        max_occurances = 0
        for month, occurances in most_common:
            if occurances < max_occurances:
                break
        
            if max_occurances == 0:
                max_occurances = occurances

            month_list.append(month)
    return month_list