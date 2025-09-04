from rest_framework import serializers
from .models import Country, Manufacture, Car, Comment

class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Country"""
    manufactures = serializers.SerializerMethodField() # Требование: При запросе страны на стороне сериализатора добавить производителей в выдачу, которые ссылаются на нее

    class Meta:
        model = Country
        fields = ['id', 'name', 'manufactures']

    def get_manufactures(self, obj):
        """Возвращает список производителей страны"""
        return [manufacture.name for manufacture in obj.manufactures.all()] # по related_name
    
class ManufactureSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Manufacture"""
    country_name = serializers.CharField(source='country.name', read_only=True) # Требование: При запросе производителя добавлять страну
    cars = serializers.SerializerMethodField() # Требование: Добавлять автомобили
    comments_count = serializers.SerializerMethodField() # Требование: Добавлять количество комментариев

    class Meta:
        model = Manufacture
        fields = ('id', 'name', 'country_name', 'cars', 'comments_count')

    def get_cars(self, obj):
        """Возвращает список автомобилей этого производителя."""
        return [car.name for car in obj.cars.all()]

    def get_comments_count(self, obj):
        """Возвращает общее количество комментариев ко всем автомобилям производителя."""
        total_comments = 0
        for car in obj.cars.all():
            total_comments += car.comments.count()
        return total_comments
    
class CarSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Car"""
    manufacture_name = serializers.StringRelatedField() # Требование: При запросе автомобиля добавить производителя
    comments = serializers.SerializerMethodField() # Требование: Добавить комментарии
    comments_count = serializers.SerializerMethodField() # Требование: Добавить количество комментариев

    class Meta:
        model = Car
        fields = ('id', 'name', 'manufacture_name', 'release_year', 'end_year', 
                 'comments', 'comments_count')

    def get_comments(self, obj):
        """Возвращает текст комментариев к автомобилю."""
        # Получаем последние комментарии сначала
        comments = obj.comments.all().order_by('-created_at')
        return [comment.comment_text for comment in comments]

    def get_comments_count(self, obj):
        """Возвращает количество комментариев для автомобиля."""
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    # Требование: Проводить валидацию входных данных
    car_name = serializers.StringRelatedField(source='car', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'email', 'car', 'car_name', 'created_at', 'comment_text')
        read_only_fields = ('created_at', 'car_name')

    def validate_email(self, value):
        """Валидация email."""
        if not value:
            raise serializers.ValidationError("Email не может быть пустым.")
        return value

    def validate_comment_text(self, value):
        """Валидация текста комментария"""
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                "Комментарий должен содержать минимум 10 символов."
            )
        if len(value) > 1000:
            raise serializers.ValidationError(
                "Комментарий не может превышать 1000 символов."
            )
        return value

    def validate_car(self, value):
        if not Car.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Указанный автомобиль не существует.")
        return value