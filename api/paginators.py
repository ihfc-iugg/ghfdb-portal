from rest_framework.pagination import LimitOffsetPagination


class DataTablesPaginator(LimitOffsetPagination):
    max_limit = 100
    offset_query_param = 'start'
    limit_query_param = 'length'
