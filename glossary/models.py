from django.conf import settings
from django.db import models


class Term(models.Model):
    """Legacy glossary model - kept for migration compatibility.
    Active glossary functionality uses service.GlossaryTerm."""

    created_at = models.DateTimeField(auto_now_add=True)
    term = models.CharField(max_length=200)
    definition = models.TextField()
    pronunciation_hint = models.CharField(max_length=200, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'مصطلح (قديم)'
        verbose_name_plural = 'المصطلحات (قديمة)'

    def __str__(self):
        return self.term
