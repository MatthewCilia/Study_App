from django import forms
from .models import Subject, Session

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "description"]

        widgets = {
                    "name": forms.TextInput(attrs={
                        "class": "form-control",
                        "placeholder": "Subject Name",
                    }),
                    "description": forms.Textarea(attrs={
                        "class": "form-control",
                        "placeholder": "Subject Description",
                    }),
        }

class SessionForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["subject"].queryset = Subject.objects.filter(
            owner=user
        )

    class Meta:
        model = Session
        fields = ["subject", "date", "duration_minutes", "notes"]

        widgets = {
                    "subject": forms.Select(attrs={
                        "class": "form-control",
                        "placeholder": "Subject Name",
                    }),
                    "date": forms.DateInput(attrs={
                        "class": "form-control",
                        "type": "date",
                    }),

                    "duration_minutes": forms.NumberInput(attrs={
                        "class": "form-control",
                        "placeholder": "Duration (minutes)",
                        "min": 1,
                    }),

                    "notes": forms.Textarea(attrs={
                        "class": "form-control",
                        "placeholder": "Notes",
                    }),
                }

