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