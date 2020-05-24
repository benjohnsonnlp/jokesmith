from random import shuffle, randint, sample
from typing import List

from django.db import models, transaction
from django.db.models import Max, F
from django.forms.models import model_to_dict


class Session(models.Model):
    name = models.CharField(max_length=80)
    started = models.BooleanField(default=False)
    status = models.CharField(max_length=80, default='start')

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)

    def build_responses(self):
        # for now, randomly get prompts
        players = list(self.player_set.all())
        shuffle(players)
        prompts = Prompt.random_set(len(players))
        for i, player in enumerate(players):
            partner = players[(i + 1) % len(players)]
            prompt = prompts[i]
            response = Response(player=player, prompt=prompt, session=self,
                                text="")
            print("Saving {}...".format(response))
            response.save()
            response = Response(player=partner, prompt=prompt, session=self,
                                text="")
            print("Saving {}...".format(response))
            response.save()


class Player(models.Model):
    name = models.CharField(max_length=80)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    is_ready = models.BooleanField(default=False)
    submitted_prompts = models.BooleanField(default=False)
    voted = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ("name", "session")

    def __str__(self):
        return self.name

    def dict(self):
        return model_to_dict(self)

    def get_unanswered_questions(self):
        if len(self.session.response_set.all()) == 0:
            self.session.build_responses()
        responses = list(self.response_set.filter(text="", session=self.session))
        return responses

    # @transaction.atomic
    def increase_score(self):
        self.refresh_from_db()
        print("{}'s score is {}".format(self.name, self.score))
        self.score = F('score') + 1
        self.save()
        self.refresh_from_db()
        print("{}'s score increased to {}".format(self.name, self.score))


class Prompt(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Player, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        if len(self.text) > 32:
            return self.text[:32] + "..."
        return self.text

    def dict(self):
        return model_to_dict(self)

    @staticmethod
    def random_set(n: int) -> List["Prompt"]:
        """
        Return a random set of ``n`` prompts. Use when we need to do "sampling without replacement." Note that if ``n``
        is larger than the available prompts, what we do have will be replicated until we have all prompts we need.
        """
        all_ids = list(Prompt.objects.all().values_list("id", flat=True))
        if not all_ids:
            starter_prompts = [
                "Weird thing to say to in-laws",
                "Rejected pop-tart flavors",
                "Worst news to get via carrier pigeon",
            ]
            for prompt in starter_prompts:
                p = Prompt(text=prompt, author=None)
                p.save()
            all_ids = list(Prompt.objects.all().values_list("id", flat=True))

        sample_ids = sample(all_ids, min(n, len(all_ids)))
        prompts = list(Prompt.objects.filter(id__in=sample_ids))
        for i in range(n - len(prompts)):
            prompts.append(prompts[i])
        return prompts

    @staticmethod
    def random():
        """
        Get a single random prompt.
        """
        max_id = Prompt.objects.all().aggregate(max_id=Max("id"))["max_id"]
        if not max_id:
            # raise ValueError("No prompts in DB")
            prompt = Prompt(text="Test prompt", author=None)
            prompt.save()
            return prompt
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
        output = model_to_dict(self)
        output['player_name'] = self.player.name
        return output

    def __str__(self):
        player_name = self.player.name if self.player else "unknown-player"
        session_name = self.session.name if self.session else "unknown-session"
        return "Response for player {} with text '{}' for session {}".format(
            player_name,
            self.text,
            session_name,
        )


class Vote(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)

    def dict(self):
        output = model_to_dict(self)
        output['player_name'] = self.player.name
        return output
