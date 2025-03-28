from django.contrib import admin
from .models import CandidateRanking

@admin.register(CandidateRanking)
class CandidateRankingAdmin(admin.ModelAdmin):
    list_display = ("fullname", "email", "score", "created_at")
    search_fields = ("fullname", "email")
    ordering = ("-score",)
