from django.contrib import admin
from .models import Country, Manufacture, Car, Comment

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Админка для стран"""
    list_display = ('id', 'name')
    search_fields = ('name',)  # Поиск по названию
    ordering = ('name',)  # Сортировка по названию

@admin.register(Manufacture)
class ManufactureAdmin(admin.ModelAdmin):
    """Админка для производителей"""
    list_display = ('id', 'name', 'country')
    list_filter = ('country',)  # Фильтр по странам
    search_fields = ('name', 'country__name')
    ordering = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    """Админка для автомобилей"""
    list_display = ('id', 'name', 'manufacture', 'release_year', 'end_year')
    list_filter = ('manufacture', 'release_year')
    search_fields = ('name', 'manufacture__name')
    ordering = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев"""
    list_display = ('id', 'email', 'car', 'created_at')
    list_filter = ('created_at', 'car')  # Фильтр по дате и автомобилю
    search_fields = ('email', 'car__name', 'comment_text')
    readonly_fields = ('created_at',)  # Дата создания только для чтения
    ordering = ('-created_at',)  # Сначала новые комментарии