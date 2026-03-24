from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import React
from .serializer import ReactSerializer

# Create your views here.

def home(request):
    return render(request, "home.html")

def about(request):
    return HttpResponse("About Page")

class ReactView(APIView):
    serializer_class = ReactSerializer

    def get(self, request):
        detail = [
            {"employee": obj.employee, "department": obj.department}
            for obj in React.objects.all()
        ]
        return Response(detail)

    def post(self, request):
        serializer = ReactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)