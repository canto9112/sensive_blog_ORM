from django.db.models import Count
from django.shortcuts import render

from blog.models import Post, Tag


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def index(request):
    all_posts = Post.objects.prefetch_tags_and_author_with_comments_count()

    popular_posts = all_posts.popular()[:5].comments_count()
    fresh_posts = all_posts.annotate(comments_count=Count('comments')).order_by('-published_at')[:5]

    popular_tags = Tag.objects.popular()[:5].annotate(Count('posts'))

    context = {
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    all_posts = Post.objects.prefetch_tags_and_author_with_comments_count()
    post = all_posts.annotate(Count('likes')).get(slug=slug)
    comments = post.comments.prefetch_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': post.likes__count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    popular_tags = Tag.objects.popular()[:5].annotate(Count('posts'))
    popular_posts = all_posts.popular()[:5].comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    popular_tags = Tag.objects.popular()[:5].annotate(Count('posts'))
    all_posts = Post.objects.prefetch_tags_and_author_with_comments_count()
    popular_posts = all_posts.popular()[:5].comments_count()

    related_posts = all_posts.filter(tags=tag)[:20].comments_count()
    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})