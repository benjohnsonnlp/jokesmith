from django.db import models
from django.forms.models import model_to_dict


# Create your models here.
class Session(models.Model):
    name = models.CharField(max_length=80)
    started = models.BooleanField(default=False)

    def dict(self):
        return model_to_dict(self)


class Player(models.Model):
    name = models.CharField(max_length=80)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    is_ready = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "session")

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)


class Question(models.Model):
    text = models.TextField()


class Prompt(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Response(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    text = models.TextField()
