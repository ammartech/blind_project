from django.contrib import admin

from .models import GlossaryCategory, GlossaryTerm, Inquiry


@admin.register(GlossaryCategory)
class GlossaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'term_count', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'question_text', 'transcription_text', 'answer_text')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('term', 'category', 'view_count', 'tts_play_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('term', 'definition')
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'tts_play_count')
