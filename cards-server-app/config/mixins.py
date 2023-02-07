from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination


class EagerLoadingViewSetMixin:
    """
        Eager Loading ViewSet Mixin
        ---
        - Override `get_queryset` of Rest Framework View Set class
            - call `serializer.setup_eager_loading` to pre-fecth and select related
            - required function `serializer.setup_eager_loading`
        - examples:
            - BookViewSetV1: demo_manager/views/book.py
                - BookSerializer:  demo_manager/serializers/book.py
    """

    def get_queryset(self):
        serializer = self.get_serializer_class()
        if not hasattr(serializer, "setup_eager_loading"):
            raise NotImplementedError(
                "{} is missing function setup_eager_loading.".format(
                    serializer.__name__
                )
            )
        _queryset = self.queryset
        _queryset = serializer.setup_eager_loading(_queryset)
        return _queryset


class DefaultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100
    page_size_query_param = "page_size"
    page_query_description = _('A page number within the paginated result set. page "-1" would return a list result '
                               'without paginated')


class PaginationListViewSetMixin:
    """
    Pagination List ViewSet Mixin
    ---
    - Using Rest Framework Pagination Class
        - The page number start at 1
        - If page is -1 it would return results list without Pagination
        - Supports override `page_size` with `OVERRIDE_PAGE_SIZE`
    - Supports search, and django-filter filter backends
        These fields are required to enable filter backend
        - django-filter:
            filterset_fields = {
                <field_name>: Array<queryset_filter_type>,  # (i.e. "exact", "icontains")
            }
        - search:
            search_fields = Array<field_name>
    """
    pagination_class = DefaultPagination

    # Override pagination settings
    OVERRIDE_PAGE_SIZE = None

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]

    @property
    def paginator(self):
        """
        Override rest framework GenericAPIView paginator property
        ---
            The paginator instance associated with the view, or `None`
            and override pagination settings if it's not `None`.
        """
        _ = super().paginator

        if self._paginator and self.OVERRIDE_PAGE_SIZE is not None:
            self._paginator.page_size = self.OVERRIDE_PAGE_SIZE

        return self._paginator

    def get_paginator_page_query_param(self):
        if not getattr(self, "paginator", None) or not self.paginator:
            raise NotImplementedError(
                "{} is missing Rest Framework the Pagination class.".format(
                    self.__class__.__name__
                )
            )

        return self.paginator.page_query_param

    def get_page_number_in_query_param(self, request) -> str:
        page_key = self.get_paginator_page_query_param()
        return str(request.query_params.get(page_key, ""))

    def list(self, request, *args, **kwargs):
        # Remove pagination_class and _paginator if request page is -1
        if self.get_page_number_in_query_param(request) == "-1":
            self.pagination_class = None
            self._paginator = None

        return super().list(request, args, kwargs)


class PaginationWithEagerLoadingViewSetMixin(EagerLoadingViewSetMixin, PaginationListViewSetMixin):
    """
    Pagination with Eager Loading ViewSet Mixin
    """


# Admin
class EagerLoadingAnnotatesAdminChangeListMixin(ChangeList):
    """
    EagerLoadingAnnotatesAdminChangeListMixin
    ---
    Annotates model queryset to display ManyToMany related in list_display without several hit database
    ---
    Instruction
    1. Create new EagerLoadingAnnotatesChangeList class
    2. Implement function annotates_queryset
    3. Override AdminView function get_changelist
        def get_changelist(self, request, **kwargs):
            return EagerLoadingAnnotatesChangeList
    ---
    examples:
        BookAdminView: demo_manager/admin/book.py
        BookChangeList: demo_manager/admin/book.py
    """
    def annotates_queryset(self, queryset):
        raise NotImplementedError(
            "{} is missing function annotates_queryset.".format(
                self.__class__.__name__
            )
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = self.annotates_queryset(queryset)
        return queryset


class EagerLoadingAdminChangeListMixin(ChangeList):
    """
    EagerLoadingAdminChangeListMixin
    ---
    Catching model queryset to display OneToOne, ManyToOne related in list_display without several hit database
    ---
    Instruction
    1. Create new EagerLoadingAdminChangeList class
    2. Implement function setup_eager_loading
    3. Override AdminView function get_changelist
        def get_changelist(self, request, **kwargs):
            return EagerLoadingAdminChangeList
    ---
    examples:
        ProfileAdminView: user_manager/admin.py
        ProfileChangeList: user_manager/admin.py
    """
    def setup_eager_loading(self, queryset):
        raise NotImplementedError(
            "{} is missing function setup_eager_loading.".format(
                self.__class__.__name__
            )
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = self.setup_eager_loading(queryset)
        return queryset
