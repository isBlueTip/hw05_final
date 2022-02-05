from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Adds the date of creation."""
    pub_date = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        abstract = True
        ordering = ['-pub_date']
