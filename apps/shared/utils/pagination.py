from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class StandardPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
    page_size_query_param = "page_size"
    max_page_size = settings.REST_FRAMEWORK["MAX_PAGE_SIZE"]
