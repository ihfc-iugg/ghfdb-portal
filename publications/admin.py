from django.contrib import admin

# #Register your models here.
# @admin.register(Operator)
# class OperatorAdmin(admin.ModelAdmin):
#     counts = ['site_count',]
#     list_display = ['name',] + counts
#     search_fields = ('name',)
#     exclude = ['added_by','edited_by']
    
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         queryset = queryset.annotate(
#             _site_count=Count("sites", distinct=True),
#            )
#         return queryset

#     def site_count(self,obj):
#         return obj._site_count
#     site_count.admin_order_field = '__site_count'

