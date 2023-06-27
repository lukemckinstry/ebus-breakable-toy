from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .serializers import AgencySerializer, RouteSerializer, RouteBatchSerializer, DataSourceSerializer, DataSourceUpdateSerializer
from .models import Agency, Route, DataSource
from rest_framework import viewsets, permissions, status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response



def index(request):
    return HttpResponse("Hello, world. You're at the routes index.")


def basic_map(request):
    # return basic map

    # TODO: move this token to Django settings from an environment variable
    # found in the Mapbox account settings and getting started instructions
    # see https://www.mapbox.com/account/ under the "Access tokens" section
    return render(request, "transit/index.html")


def route_bbox(request, pk):
    r = Route.objects.get(id=pk).geometry.extent
    return JsonResponse({"bbox": r})


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    Viewset to automatically provide the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

class DataSourceUpdateView(UpdateAPIView):
    """
    Viewset to automatically provide the `update` action.
    """

    queryset = DataSource.objects.all()
    serializer_class = DataSourceUpdateSerializer

class AgencyViewSet(viewsets.ModelViewSet):
    """
    Viewset to automatically provide the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    queryset = Agency.objects.all()
    serializer_class = AgencySerializer

    def get_queryset(self):
        print("here")
        data_source = self.kwargs.get("datasource_pk")
        if not data_source:
            return Agency.objects.all()  # all other requests
        queryset = Agency.objects.filter(data_source=data_source)
        return queryset
    
    def create(self, request, pk):
        agency_copy = {**request.data}
        agency_copy = {**agency_copy, "data_source": pk}
        serializer = self.get_serializer_class()
        try:
            agency_instance = Agency.objects.get(data_source=pk,agency_id=agency_copy["agency_id"])
            agency_to_post = serializer(instance=agency_instance,data=agency_copy)
        except Agency.DoesNotExist:
            agency_to_post = serializer(data=agency_copy)
        if agency_to_post.is_valid():
            agency_to_post.save()
            return Response(agency_to_post.data, status=status.HTTP_201_CREATED)
        print(agency_to_post.errors)
        return Response(agency_to_post.errors, status=status.HTTP_400_BAD_REQUEST)

class RouteViewSet(viewsets.ModelViewSet):
    """
    Viewset to automatically provide the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        agency = self.kwargs.get("agency_pk")  # supports get request by agency endpoint
        if not agency:
            return Route.objects.all()  # all other requests
        queryset = Route.objects.filter(agency=agency)
        return queryset
    

class RouteBatchViewSet(viewsets.ModelViewSet):
    """
    Viewset for the batch upload process to automatically provide the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    serializer_class = RouteBatchSerializer
    ## ToDo: Add permissions
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        agency = self.kwargs.get("agency_pk")  # supports get request by agency endpoint
        if not agency:
            return Route.objects.all()  # all other requests
        queryset = Route.objects.filter(agency=agency)
        return queryset
    
    def create(self, request, agency_pk):
        route_copy = {**request.data}

        route_copy["properties"] = {**route_copy["properties"], "agency": agency_pk}
        serializer = self.get_serializer_class()
        # POST supports upsert functionality 
        try:
            route_instance = Route.objects.get(route_id=route_copy["properties"]["route_id"],agency=agency_pk)
            route_to_post = serializer(instance=route_instance,data=route_copy)
        except Route.DoesNotExist:
            route_to_post = serializer(data=route_copy)
        if route_to_post.is_valid():
            route_to_post.save()
            return Response(route_to_post.data, status=status.HTTP_201_CREATED)
        return Response(route_to_post.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk):
        route = Route.objects.get(id=pk) 
        route_copy = {**request.data}
        route_copy["properties"] = {**route_copy["properties"], "route": route.id, "agency": route.agency.id}
        serializer = self.get_serializer_class()
        route_to_update = serializer(route, data=route_copy)
        if route_to_update.is_valid():
            route_to_update.save()
            return Response(route_to_update.data, status=status.HTTP_200_OK)
        return Response(route_to_update.errors, status=status.HTTP_400_BAD_REQUEST)
