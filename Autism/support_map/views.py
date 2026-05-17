from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from .models import AutismSupportPlace
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PlaceLike

# Create your views here.

def support_map_view (request:HttpRequest):
    places = AutismSupportPlace.objects.all()

    return render(request,'support_map/support-map.html',{'places': places})

def create_place_view (request:HttpRequest):
    if request.method == "POST":

        AutismSupportPlace.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            region=request.POST.get("region"),
            address=request.POST.get("address"),
            phone_number=request.POST.get("phone_number"),
            website=request.POST.get("website"),
            place_type=request.POST.get("place_type"),
        )

        return redirect("map:support_map_view")

    return render(request,'support_map/create_place.html', {"regions": AutismSupportPlace.REGIONS,"place_types": AutismSupportPlace.PLACE_TYPES})


def edit_place_view(request, place_id):

    place = get_object_or_404(
        AutismSupportPlace,
        id=place_id
    )

    if request.method == "POST":

        place.name = request.POST.get("name")
        place.description = request.POST.get("description")
        place.region = request.POST.get("region")
        place.address = request.POST.get("address")
        place.phone_number = request.POST.get("phone_number")
        place.website = request.POST.get("website")
        place.place_type = request.POST.get("place_type")

        place.save()

        return redirect("map:support_map_view")

    return render(request, 'support_map/edit_place.html',{
            "place": place,
            "regions": AutismSupportPlace.REGIONS,
            "place_types": AutismSupportPlace.PLACE_TYPES
        })

def delete_place_view(request, place_id):

    place = get_object_or_404(AutismSupportPlace,id=place_id)
    place.delete()

    return redirect("map:support_map_view")

def support_map_view(request: HttpRequest):

    search = request.GET.get("search", "")

    places = AutismSupportPlace.objects.all()
    type_map = {
    "حكومي": "government",
    "خاص": "private",
    "مجتمعي": "community",}
    mapped_type = type_map.get(search.strip())

    if search:

        places = places.filter(
            Q(name__icontains=search) |
            Q(place_type=mapped_type)
        )

    return render(
        request,
        'support_map/support-map.html',
        {
            'places': places
        }
    )
    
@login_required
def toggle_like_view(request, place_id):

    place = get_object_or_404(AutismSupportPlace,id=place_id)
    like = PlaceLike.objects.filter(user=request.user,place=place).first()

    if like:
        like.delete()
        liked = False

    else:
        PlaceLike.objects.create(user=request.user,place=place)
        liked = True
    return JsonResponse({
        "liked": liked
    })




    