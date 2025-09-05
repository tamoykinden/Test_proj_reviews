from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from .models import Country, Manufacture, Car, Comment
from .serializers import CountrySerializer, ManufactureSerializer, CarSerializer, CommentSerializer
from .permissions import HasAPIAccessToken

class ExportMixin:
    """Миксин для экспорта данных в CSV и XLSX форматах"""
    
    def export_to_csv(self, data, filename, headers, row_callback):
        """Генерация CSV файла"""
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
        )
        
        writer = csv.writer(response)
        writer.writerow(headers)
        
        for item in data:
            writer.writerow(row_callback(item))
        
        return response

    def export_to_xlsx(self, data, filename, headers, row_callback):
        """Генерация Excel файла"""
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{filename}.xlsx"'},
        )
        
        wb = Workbook()
        ws = wb.active
        ws.title = filename
        ws.append(headers)
        
        for item in data:
            ws.append(row_callback(item))
        
        wb.save(response)
        return response

class CountryViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования стран.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Country.objects.all().prefetch_related('manufactures')
    serializer_class = CountrySerializer
    permission_classes = [HasAPIAccessToken]

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных о странах"""
        format_type = request.GET.get('format', 'csv')
        countries = Country.objects.all().prefetch_related('manufactures')
        
        headers = ['ID', 'Country Name', 'Manufactures Count', 'Manufactures List']
        
        def country_row_callback(country):
            manufactures_list = ', '.join([m.name for m in country.manufactures.all()])
            return [
                country.id,
                country.name,
                country.manufactures.count(),
                manufactures_list
            ]
        
        if format_type == 'xlsx':
            return self.export_to_xlsx(countries, 'countries', headers, country_row_callback)
        else:
            return self.export_to_csv(countries, 'countries', headers, country_row_callback)

class ManufactureViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования производителей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Manufacture.objects.all().select_related('country').prefetch_related('cars')
    serializer_class = ManufactureSerializer
    permission_classes = [HasAPIAccessToken]

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных о производителях"""
        format_type = request.GET.get('format', 'csv')
        manufactures = Manufacture.objects.all().select_related('country').prefetch_related('cars')
        
        headers = ['ID', 'Manufacture Name', 'Country', 'Cars Count', 'Total Comments Count']
        
        def manufacture_row_callback(manufacture):
            total_comments = sum(car.comments.count() for car in manufacture.cars.all())
            return [
                manufacture.id,
                manufacture.name,
                manufacture.country.name,
                manufacture.cars.count(),
                total_comments
            ]
        
        if format_type == 'xlsx':
            return self.export_to_xlsx(manufactures, 'manufactures', headers, manufacture_row_callback)
        else:
            return self.export_to_csv(manufactures, 'manufactures', headers, manufacture_row_callback)

class CarViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования автомобилей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
    serializer_class = CarSerializer
    permission_classes = [HasAPIAccessToken]

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных об автомобилях"""
        format_type = request.GET.get('format', 'csv')
        cars = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
        
        headers = ['ID', 'Model', 'Manufacture', 'Country', 'Start Year', 'End Year', 'Comments Count']
        
        def car_row_callback(car):
            return [
                car.id,
                car.name,
                car.manufacture.name,
                car.manufacture.country.name,
                car.release_year,
                car.end_year or 'Present',
                car.comments.count()
            ]
        
        if format_type == 'xlsx':
            return self.export_to_xlsx(cars, 'cars', headers, car_row_callback)
        else:
            return self.export_to_csv(cars, 'cars', headers, car_row_callback)

class CommentViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    ViewSet для комментариев.
    Просмотр и добавление - публичные, изменение - по токену.
    """
    queryset = Comment.objects.all().select_related('car', 'car__manufacture', 'car__manufacture__country')
    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Настраиваем права доступа в зависимости от действия:
        - create, list, retrieve: публичный доступ
        - update, partial_update, destroy: по токену
        """
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [HasAPIAccessToken]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Экспорт данных о комментариях"""
        format_type = request.GET.get('format', 'csv')
        comments = Comment.objects.all().select_related('car', 'car__manufacture', 'car__manufacture__country')
        
        headers = ['ID', 'Email', 'Car', 'Manufacture', 'Country', 'Created At', 'Comment Text']
        
        def comment_row_callback(comment):
            return [
                comment.id,
                comment.email,
                comment.car.name,
                comment.car.manufacture.name,
                comment.car.manufacture.country.name,
                comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                comment.comment_text[:100] + '...' if len(comment.comment_text) > 100 else comment.comment_text
            ]
        
        if format_type == 'xlsx':
            return self.export_to_xlsx(comments, 'comments', headers, comment_row_callback)
        else:
            return self.export_to_csv(comments, 'comments', headers, comment_row_callback)
