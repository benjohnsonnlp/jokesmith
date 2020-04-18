from django.db import models


# Create your models here.
class Session(models.Model):
    name = models.CharField(max_length=80)


class Player(models.Model):
    name = models.CharField(max_length=80)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)


class Question(models.Model):
    text = models.TextField()


class Prompt(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Response(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    text = models.TextField()