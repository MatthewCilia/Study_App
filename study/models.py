from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Subject(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_subject_per_user"
            )
        ]

    def __str__(self):
        return self.name

class Session(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.date}"

