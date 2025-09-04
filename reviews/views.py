from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from .models import Country, Manufacture, Car, Comment
from .serializers import CountrySerializer, ManufactureSerializer, CarSerializer, CommentSerializer

class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования стран.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Country.objects.all().prefetch_related('manufactures')
    serializer_class = CountrySerializer


class ManufactureViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования производителей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Manufacture.objects.all().select_related('country').prefetch_related('cars')
    serializer_class = ManufactureSerializer


class CarViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования автомобилей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
    serializer_class = CarSerializer

    # Требование: Экспорт данных в формате xlsx + csv
    @action(detail=False, methods=['get'])
    def export(self, request):
        """ endpoint для экспорта данных об автомобилях."""
        format_type = request.GET.get('format', 'csv').lower()

        # данные с оптимизацией запросов
        cars = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
        
        if format_type == 'xlsx':
            return self.export_to_xlsx(cars)
        else:
            return self.export_to_csv(cars)

    def export_to_csv(self, cars):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="cars_export.csv"'},
        )
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Model', 'Manufacture', 'Country', 'Start year', 'End year', 'Comments Count'])
        
        for car in cars:
            writer.writerow([
                car.id,
                car.name,
                car.manufacture.name,
                car.manufacture.country.name,
                car.release_year,
                car.end_year or 'Present',
                car.comments.count()
            ])
        
        return response

    def export_to_xlsx(self, cars):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="cars_export.xlsx"'},
        )
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Cars"
        
        headers = ['ID', 'Model', 'Manufacture', 'Country', 'Start year', 'End year', 'Comments Count']
        ws.append(headers)
        
        for car in cars:
            ws.append([
                car.id,
                car.name,
                car.manufacture.name,
                car.manufacture.country.name,
                car.release_year,
                car.end_year or 'Present',
                car.comments.count()
            ])
        
        wb.save(response)
        return response


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для комментариев.
    Просмотр и добавление - публичные, изменение - по токену.
    """
    queryset = Comment.objects.all().select_related('car')
    serializer_class = CommentSerializer
