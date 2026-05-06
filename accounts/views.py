from django.shortcuts import render
from django.http import JsonResponse
from .models import City


def get_cities(request):
    governorate_id = request.GET.get("governorate_id")
    if not governorate_id:
        return JsonResponse({"cities": []})
    
    cities = City.objects.filter(
        governorate_id=governorate_id,
        is_active=True
    ).values("id", "name_ar", "name_en", "shipping_cost")
    
    return JsonResponse({"cities": list(cities)})
