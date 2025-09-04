from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from .models import Country, Manufacture, Car, Comment
from .serializers import CountrySerializer, ManufactureSerializer, CarSerializer, CommentSerializer
from .permissions import HasAPIAccessToken

class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования стран.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Country.objects.all().prefetch_related('manufactures')
    serializer_class = CountrySerializer
    permission_classes = [HasAPIAccessToken]


class ManufactureViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования производителей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Manufacture.objects.all().select_related('country').prefetch_related('cars')
    serializer_class = ManufactureSerializer
    permission_classes = [HasAPIAccessToken]


class CarViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования автомобилей.
    Доступ к изменяющим операциям только по токену.
    """
    queryset = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
    serializer_class = CarSerializer
    permission_classes = [HasAPIAccessToken]

    @action(detail=False, methods=['get'], url_path='export/csv')
    def export_csv(self, request):
        """Экспорт данных об автомобилях в CSV формате."""
        cars = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
        return self.export_to_csv(cars)

    @action(detail=False, methods=['get'], url_path='export/xlsx')
    def export_xlsx(self, request):
        """Экспорт данных об автомобилях в Excel формате."""
        cars = Car.objects.all().select_related('manufacture', 'manufacture__country').prefetch_related('comments')
        return self.export_to_xlsx(cars)

    def export_to_csv(self, cars):
        """Генерация CSV файла."""
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="cars_export.csv"'},
        )
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Model', 'Manufacture', 'Country', 'Start Year', 'End Year', 'Comments Count'])
        
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
        """Генерация Excel файла."""
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="cars_export.xlsx"'},
        )
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Cars"
        
        headers = ['ID', 'Model', 'Manufacture', 'Country', 'Start Year', 'End Year', 'Comments Count']
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

    def get_permissions(self):
        """
        Настраиваем права доступа в зависимости от действия:
        - create, list, retrieve: публичный доступ
        - update, partial_update, destroy: по токену
        """
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = []  # AllowAny по умолчанию
        else:
            permission_classes = [HasAPIAccessToken]
        return [permission() for permission in permission_classes]
