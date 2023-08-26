from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный класс пагинации."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
