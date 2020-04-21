from django.contrib import admin

from jokes.models import Player, Prompt, Response, Session


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):

    list_display = ("name", "session", "is_ready", "submitted_prompts")
    list_filter = ("is_ready", "submitted_prompts")
    search_fields = ("name",)


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):

    list_display = ("text", "author")
    search_fields = ("text",)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("player", "prompt", "session", "text")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("name", "started")
