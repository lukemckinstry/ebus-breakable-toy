from django.http import HttpResponse, JsonResponse

from .serializers import AgencySerializer, RouteSerializer
from .models import Agency, Route

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status


def index(request):
    return HttpResponse("Hello, world. You're at the routes index.")

@api_view(['GET','POST'])
def route_list(request, agency_id):
    """   List agencies """

    if request.method == 'GET':
        data = []
        nextPage = 1
        previousPage = 1
        start = request.GET.get('start', 0)
        try:
            qs = Route.objects.filter(agency_id__agency_id=agency_id).order_by('route_short_name')[int(start):int(start)+20]
        except Agency.DoesNotExist:
            return HttpResponse(status=404)
        serializer = RouteSerializer(qs,context={'request': request} ,many=True)
        return Response({'data': serializer.data})

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = RouteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET','PUT','DELETE'])
def route_detail(request, route_id):
    """   Retrieve, update or delete a route """

    try:
        qs = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = RouteSerializer(qs,context={'request': request})
        return Response({'data': serializer.data})

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = RouteSerializer(qs, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        qs.delete()
        return HttpResponse(status=204)

@api_view(['GET','POST'])
def agency_list(request):
    """   List agencies """

    if request.method == 'GET':
        data = []
        nextPage = 1
        previousPage = 1
        qs = Agency.objects.all().order_by('created')[:30]
        serializer = AgencySerializer(qs,context={'request': request} ,many=True)
        return Response({'data': serializer.data})

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AgencySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=400)


@api_view(['GET','PUT','DELETE'])
def agency_detail(request, agency_id):
    """   Retrieve, update or delete an agency """

    try:
        qs = Agency.objects.get(agency_id=agency_id)
    except Agency.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AgencySerializer(qs,context={'request': request})
        return Response({'data': serializer.data})

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AgencySerializer(qs, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        qs.delete()
        return HttpResponse(status=204)