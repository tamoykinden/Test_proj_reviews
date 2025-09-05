from rest_framework import serializers
from .models import Country, Manufacture, Car, Comment
from django.core.exceptions import ValidationError

class CountrySerializer(serializers.ModelSerializer):
    # Требование: При запросе страны на стороне сериализатора добавить производителей в выдачу, которые ссылаются на нее
    manufactures = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'manufactures']

    def get_manufactures(self, obj):
        """Возвращает список производителей, связанных с этой страной"""
        if hasattr(obj, 'manufactures'):
            return [manufacture.name for manufacture in obj.manufactures.all()]
        return []

    def validate_name(self, value):
        """Валидация названия страны с учетом уникальности"""
        value = value.strip()
        # Проверяю, существует ли страна с таким названием (игнорируя регистр)
        if Country.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Страна с таким названием уже существует")
        return value
    
class ManufactureSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Manufacture"""
    # Требование: При запросе производителя добавлять страну, автомобили и количество комментариев к ним к выдаче
    country_name = serializers.CharField(source='country.name', read_only=True)
    cars = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Manufacture
        fields = ('id', 'name', 'country', 'country_name', 'cars', 'comments_count')

    def get_cars(self, obj):
        """Возвращает список автомобилей этого производителя"""
        return [car.name for car in obj.cars.all()]

    def get_comments_count(self, obj):
        """Возвращает общее количество комментариев ко всем автомобилям производителя"""
        total_comments = 0
        for car in obj.cars.all():
            total_comments += car.comments.count()
        return total_comments

    def validate_name(self, value):
        """Валидация названия производителя с учетом уникальности"""
        value = value.strip()
        if Manufacture.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Производитель с таким названием уже существует")
        return value

    
class CarSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Car"""
    # Требование: При запросе автомобиля добавить производителя и комментарии с их количеством в выдачу
    manufacture_name = serializers.CharField(source='manufacture.name', read_only=True)
    comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ('id', 'name', 'manufacture', 'manufacture_name', 'release_year', 'end_year', 
                 'comments', 'comments_count')

    def get_comments(self, obj):
        """Возвращает текст комментариев к автомобилю"""
        comments = obj.comments.all().order_by('-created_at')
        return [comment.comment_text for comment in comments]

    def get_comments_count(self, obj):
        """Возвращает количество комментариев к автомобилю"""
        return obj.comments.count()

    def validate_name(self, value):
        """Валидация названия автомобиля с учетом уникальности"""
        value = value.strip()
        if Car.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Автомобиль с таким названием уже существует")
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment"""
    # Требование: При добавлении комментария проводить валидацию входных данных
    car_name = serializers.StringRelatedField(source='car', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'email', 'car', 'car_name', 'created_at', 'comment_text')
        read_only_fields = ('created_at', 'car_name')

    def validate_email(self, value):
        """Валидация email."""
        if not value:
            raise serializers.ValidationError("Email не может быть пустым")
        return value

    def validate_comment_text(self, value):
        """Валидация текста комментария"""
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                "Комментарий должен содержать минимум 10 символов"
            )
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Комментарий не может превышать 1000 символов"
            )
        return value

    def validate_car(self, value):
        """Валидация существования автомобиля"""
        if not Car.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Указанный автомобиль не существует")
        return value
    