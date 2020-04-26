from random import random, shuffle, randint

from django.db import models
from django.db.models import Max
from django.forms.models import model_to_dict


class Session(models.Model):
    name = models.CharField(max_length=80)
    started = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)

    def build_responses(self):
        # for now, randomly get prompts
        players = list(self.player_set.all())
        shuffle(players)
        for i in range(len(players)):
            player = players[i]
            partner = players[(i + 1) % len(players)]
            prompt = Prompt.random()
            response = Response(player=player, prompt=prompt, session=self, text="")
            response.save()
            response = Response(player=partner, prompt=prompt, session=self, text="")
            response.save()





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

    def get_unanswered_questions(self):
        if len(self.session.response_set.all()) == 0:
            self.session.build_responses()
        responses = self.response_set.filter(text="")
        return responses


class Prompt(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if len(self.text) > 32:
            return self.text[:32] + "..."
        return self.text

    def dict(self):
        return model_to_dict(self)

    @staticmethod
    def random():
        max_id = Prompt.objects.all().aggregate(max_id=Max("id"))["max_id"]
        if max_id < 1:
            raise ValueError("No prompts in DB")
        while True:
            pk = randint(1, max_id)
            prompt = Prompt.objects.filter(pk=pk).first()
            if prompt:
                return prompt




class Response(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    text = models.TextField()

    def dict(self):
        return model_to_dict(self)
