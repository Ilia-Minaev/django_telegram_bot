from django.db import models



class UserModels(models.Model):
    firstname = models.CharField(max_length=256, blank=False, verbose_name='Имя')
    lastname = models.CharField(max_length=256, blank=False, verbose_name='Фамилия')
    phone = models.PositiveIntegerField(blank=False, verbose_name='Номер телефона')
    external_id = models.PositiveIntegerField(unique=True, verbose_name='Telegram ID')

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class UserMessageModels(models.Model):
    user_id = models.ForeignKey(to=UserModels, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024)