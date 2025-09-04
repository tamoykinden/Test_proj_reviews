from django.db import models

class  Country(models.Model):
    """Модель стран производителей"""

    name = models.CharField(max_length=30, verbose_name='Название страны', help_text='Введите название страны')

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name']

    def __str__(self):
        return self.name

class Manufacture(models.Model):
    """Модель производителей"""

    name = models.CharField(max_length=150, verbose_name='Название производителя', help_text='Введите название производителя')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='manufactures', help_text='Выберите страну производителя')

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']

    def __str__(self):
        return f'Производитель {self.name} из страны {self.country}'
    
class Car(models.Model):
    """Модель автомобилей"""

    name = models.CharField(max_length=100, verbose_name='Автомобиль', help_text='Введите название модели автомобиля')
    manufacture = models.ForeignKey(Manufacture, on_delete=models.CASCADE, related_name='cars', help_text='Выберите производителя')
    release_year = models.PositiveIntegerField(verbose_name='Год начала выпуска')
    end_year = models.PositiveIntegerField(verbose_name='Год окончания выпуска', null=True, blank=True, help_text='Оставьте поле пустым, если автомобиль еще выпускается')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.manufacture}), {self.release_year} - {self.end_year or 'н.в'}"
    
class Comment(models.Model):
    """Модель комментариев"""

    email = models.EmailField(verbose_name='Email автора')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='comments', verbose_name='Автомобиль')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    comment_text = models.TextField(max_length=1000, verbose_name='Текст комментария', help_text='Максимальная длина коммента - 1000 символов')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий "{self.comment_text}" от {self.email} к {self.car}'
