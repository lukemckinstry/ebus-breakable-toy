from django.http import HttpResponse
from .models import Agency

from rest_framework.response import Response
from .serializers import *
from rest_framework.decorators import api_view


def index(request):
    return HttpResponse("Hello, world. You're at the routes index.")

@api_view(['GET'])
def agency_list(request):
    """   List agencies """

    if request.method == 'GET':
        data = []
        nextPage = 1
        previousPage = 1
        qs = Agency.objects.all().order_by('created')[:30]
        serializer = AgencySerializer(qs,context={'request': request} ,many=True)
        return Response({'data': serializer.data})

@api_view(['GET'])
def agency_detail(request, id):
    """   Show agency """

    try:
        qs = Agency.objects.get(agency_id=id)
    except Agency.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AgencySerializer(qs,context={'request': request})
        return Response({'data': serializer.data})