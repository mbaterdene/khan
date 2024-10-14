import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.cache import cache
from django.conf import settings
from django.db.models import Count
from django.urls import reverse
from django.core.paginator import Paginator

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from notifications.models import Notification
from blog.models import Blog, BlogType

def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1) # Get url page parameters (GET request)
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num = page_of_blogs.number # Get the current page number
    # Get the page range of 2 pages before and after the current page number
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # Add omitted page number mark
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # Add first and last pages
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # Get the number of blogs corresponding to the date archive
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, 
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context

def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
                .filter(read_details__date__lt=today, read_details__date__gte=date) \
                .values('id', 'title') \
                .annotate(read_num_sum=Sum('read_details__read_num')) \
                .order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    # Get the most recent blog post
    most_recent_blog = Blog.objects.order_by('-created_time').first()
    
    # Get the next 3 blogs after the most recent one
    next_blogs = Blog.objects.order_by('-created_time')[1:4]

    context = {
        'most_recent_blog': most_recent_blog,
        'next_blogs': next_blogs,
    }
    return render(request, 'home1.html', context)

def my_notifications(request):
    context = {}
    return render(request, 'my_notifications.html', context)
    
def my_notification(request, my_notification_pk):
    my_notification = get_object_or_404(Notification, pk=my_notification_pk)
    my_notification.unread = False
    my_notification.save()
    return redirect(my_notification.data['url'])

def search(request):
    search_words = request.GET.get('wd', '').strip()
    # Participle: press space & | ~
    condition = None
    for word in search_words.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)
    
    search_blogs = []
    if condition is not None:
        # Filter: search
        search_blogs = Blog.objects.filter(condition)

    # Pagination
    paginator = Paginator(search_blogs, 20)
    page_num = request.GET.get('page', 1) # Get url page parameters (GET request)
    page_of_blogs = paginator.get_page(page_num)

    context = {}
    context['search_words'] = search_words
    context['search_blogs_count'] = search_blogs.count()
    context['page_of_blogs'] = page_of_blogs
    return render(request, 'search.html', context)