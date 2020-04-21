from django.db import models
from django.forms.models import model_to_dict


class Session(models.Model):
    name = models.CharField(max_length=80)
    started = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)


class Player(models.Model):
    name = models.CharField(max_length=80)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    is_ready = models.BooleanField(default=False)
    submitted_prompts = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "session")

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)


class Prompt(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if len(self.text) > 32:
            return self.text[:32] + "..."
        return self.text


class Response(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
