from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest, HttpResponse
from ai_analysis.models import ResourceVideo
from django.db.models import Q


# Create your views here.

def all_educational_videos_view (request:HttpRequest):

        videos = ResourceVideo.objects.filter(is_active=True)
        videos = ResourceVideo.objects.filter(
        is_active=True
    )

        category = request.GET.get('category')
        search = request.GET.get('search')

        if category and category != 'all':
            videos = videos.filter(category=category)

        if search:
            videos = videos.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return render (request, 'educational_videos/all_videos.html', { 'videos': videos})

def video_details_view(request, id):

    video = get_object_or_404(
        ResourceVideo,
        id=id
    )

    return render(request,'educational_videos/video_details.html',{'video': video})
