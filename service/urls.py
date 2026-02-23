from django.urls import path

from . import views

app_name = 'service'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Inquiries
    path('inquiry/new/', views.inquiry_new, name='inquiry_new'),
    path('inquiry/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiry/<int:pk>/transcribe/', views.inquiry_transcribe, name='inquiry_transcribe'),
    path('inquiry/<int:pk>/answer/', views.inquiry_answer, name='inquiry_answer'),
    path('inquiry/<int:pk>/status/', views.inquiry_update_status, name='inquiry_update_status'),
    path('inquiry/<int:pk>/close/', views.inquiry_close, name='inquiry_close'),

    # Glossary
    path('glossary/', views.glossary_list, name='glossary_list'),
    path('glossary/new/', views.glossary_new, name='glossary_new'),
    path('glossary/<int:pk>/', views.glossary_detail, name='glossary_detail'),
    path('glossary/<int:pk>/edit/', views.glossary_edit, name='glossary_edit'),
    path('glossary/<int:pk>/delete/', views.glossary_delete, name='glossary_delete'),
    path('glossary/<int:pk>/tts-played/', views.glossary_tts_played, name='glossary_tts_played'),

    # TTS
    path('tts/synthesize/', views.tts_synthesize, name='tts_synthesize'),
    path('tts/stream/', views.tts_stream, name='tts_stream'),
    path('tts/voices/', views.tts_voices, name='tts_voices'),
    path('inquiry/<int:pk>/tts/', views.tts_inquiry_answer, name='tts_inquiry_answer'),
    path('glossary/<int:pk>/tts/', views.tts_glossary_term, name='tts_glossary_term'),

    # Alias so {% url 'service:glossary_tts' pk %} also resolves
    path('glossary/<int:pk>/tts-audio/', views.tts_glossary_term, name='glossary_tts'),
]
