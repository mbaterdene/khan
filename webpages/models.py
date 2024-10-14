from django.db import models
from ckeditor.fields import RichTextField

class defualtInfo(models.Model):
    tag_choices = (
        (0, "Шүүгч нар"),
        (1, "Тамгын газар"),
    )
    tag = models.IntegerField(default=0, choices=tag_choices)
    info = RichTextField()
    images = models.ImageField(
        blank = True,
        upload_to = 'defaultInfo/'
    )

    def __str__(self):
        return f"Цэс : <{self.get_tag_display()}>"