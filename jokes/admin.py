from django.contrib import admin

from jokes.models import Player, Question, Prompt, Response, Session

admin.site.register(Player)
admin.site.register(Question)
admin.site.register(Prompt)
admin.site.register(Response)
admin.site.register(Session)
