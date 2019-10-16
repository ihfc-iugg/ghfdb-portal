from django.db import models

# Create your models here.
class Page(models.Model):
    name = models.CharField(max_length=150)
    content = models.TextField(blank=True)
    date_edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey("users.CustomUser",blank=True, null=True, on_delete=models.SET_NULL)

