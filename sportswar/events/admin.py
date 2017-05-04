from django.contrib import admin

from .models import Event, Watcher

admin.site.register(Event)
admin.site.register(Watcher)
