from django.shortcuts import render, redirect ,get_object_or_404
from django.http import HttpRequest, HttpResponse
from .forms import PostForm, CommentForm
from django.db.models import Q,Count
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment, CommentLike
# Create your views here.

def community_view (request:HttpResponse):
    posts = Post.objects.all().order_by('-created_at')
    sleep_count = Post.objects.filter(category='sleep').count()
    food_count = Post.objects.filter(category='food').count()
    play_count = Post.objects.filter(category='play').count()
    education_count = Post.objects.filter(category='education').count()
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
        Q(title__icontains=search) |
        Q(content__icontains=search) |
        Q(tags__icontains=search)|
        Q(user__first_name__icontains=search)
        )

    return render (request, 'community/community_feed.html', {
        'posts': posts,
        'sleep_count': sleep_count,
        'food_count': food_count,
        'play_count': play_count,
        'education_count': education_count,
        })

def create_post_view(request: HttpRequest):

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            return redirect('community:community_view')

        else:
            print(form.errors)

    else:
        form = PostForm()

    return render(request, 'community/create_post.html', {'form': form})

def details_post_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    is_liked = False

    if request.user.is_authenticated:
        is_liked = Like.objects.filter(post=post,user=request.user).exists()
    

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('community:details_post_view',post_id=post.id)
    else:
        form = CommentForm()


    return render(request,'community/details_post.html',{'post': post, 'form': form,'is_liked': is_liked,})

@login_required
def like_post_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    like_obj = Like.objects.filter(post=post, user=request.user)

    if like_obj.exists():
        like_obj.delete()
    else:
        Like.objects.create(post=post, user=request.user)

    return redirect(request.META.get('HTTP_REFERER', 'community:community_view'))

def edit_post_view(request, post_id):

    post = get_object_or_404(Post,id=post_id,user=request.user)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            instance=post)
        if form.is_valid():
            form.save()
            return redirect('community:details_post_view',post_id=post.id)

    else:
        form = PostForm(instance=post)

    return render(request,'community/edit_post.html',{'form': form})

def delete_post_view(request, post_id):
    post = get_object_or_404(Post,id=post_id,user=request.user)
    post.delete()

    return redirect('community:community_view')


def edit_comment_view(request, comment_id):

    comment = get_object_or_404(Comment,id=comment_id,user=request.user)

    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.save()

    return redirect('community:details_post_view',post_id=comment.post.id)

def delete_comment_view(request, comment_id):

    comment = get_object_or_404(Comment,id=comment_id,user=request.user)
    post_id = comment.post.id
    comment.delete()

    return redirect('community:details_post_view',post_id=post_id)


@login_required
def likes_view(request):
    liked_posts = Post.objects.filter(
        likes__user=request.user
    ).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at')

    liked_comments = Comment.objects.filter(
        comment_likes__user=request.user
    ).annotate(
        likes_count=Count('comment_likes', distinct=True)
    ).order_by('-created_at')

    return render(request, 'community/likes.html', {
        'liked_posts': liked_posts,
        'liked_comments': liked_comments,
        'liked_posts_count': liked_posts.count(),
        'liked_comments_count': liked_comments.count(),
    })


@login_required
def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    like_obj = CommentLike.objects.filter(comment=comment, user=request.user)

    if like_obj.exists():
        like_obj.delete()  
    else:
        CommentLike.objects.create(comment=comment, user=request.user)  

    return redirect(request.META.get('HTTP_REFERER') or 'community:community_view')