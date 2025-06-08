from django.contrib import admin

from .models import Company, CompanyTag, Tag


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name_ko", "name_en", "name_ja", "created_at", "updated_at")


@admin.register(CompanyTag)
class CompanyTagAdmin(admin.ModelAdmin):
    list_display = ("company", "tag", "created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "number", "created_at", "updated_at")
