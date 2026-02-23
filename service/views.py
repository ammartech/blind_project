from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AnswerForm,
    InquiryCreateForm,
    InquiryFilterForm,
    TranscribeForm,
    GlossaryTermForm,
)
from .models import Inquiry, GlossaryTerm

# service/views.py

# ============================================
# دوال مساعدة
# ============================================

def _is_librarian(user) -> bool:
    """التحقق من أن المستخدم أخصائي مكتبة"""
    return getattr(user, 'is_librarian', lambda: False)()


def _is_blind(user) -> bool:
    """التحقق من أن المستخدم كفيف"""
    return getattr(user, 'is_blind', lambda: False)()


def _get_user_stats(user):
    """إحصائيات المستخدم"""
    if _is_librarian(user):
        return {
            'total': Inquiry.objects.count(),
            'pending': Inquiry.objects.filter(status__in=['new', 'transcribed', 'in_progress']).count(),
            'answered_today': Inquiry.objects.filter(
                answered_at__date=timezone.now().date()
            ).count(),
            'my_answers': Inquiry.objects.filter(answered_by=user).count(),
        }
    else:
        user_inquiries = Inquiry.objects.filter(created_by=user)
        return {
            'total': user_inquiries.count(),
            'pending': user_inquiries.filter(status__in=['new', 'transcribed', 'in_progress']).count(),
            'answered': user_inquiries.filter(status='answered').count(),
            'unread': user_inquiries.filter(status='answered', is_read_by_user=False).count(),
        }


# ============================================
# عروض الاستفسارات
# ============================================

@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية"""
    user = request.user
    filter_form = InquiryFilterForm(request.GET)

    # تحديد الاستفسارات حسب نوع المستخدم
    if _is_librarian(user):
        inquiries = Inquiry.objects.select_related('created_by', 'answered_by').all()
    else:
        inquiries = Inquiry.objects.filter(created_by=user)

    # تطبيق الفلاتر
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        search = filter_form.cleaned_data.get('search')

        if status:
            inquiries = inquiries.filter(status=status)
        if priority:
            inquiries = inquiries.filter(priority=priority)
        if search:
            inquiries = inquiries.filter(
                Q(title__icontains=search) |
                Q(question_text__icontains=search) |
                Q(transcription_text__icontains=search)
            )

    # ترتيب حسب الأولوية والتاريخ
    priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
    inquiries = inquiries.order_by('-created_at')

    # الصفحات
    paginator = Paginator(inquiries, 10)
    page = request.GET.get('page', 1)
    inquiries_page = paginator.get_page(page)

    # الإحصائيات
    stats = _get_user_stats(user)

    context = {
        'inquiries': inquiries_page,
        'filter_form': filter_form,
        'stats': stats,
        'is_librarian': _is_librarian(user),
    }
    return render(request, 'service/dashboard.html', context)


@login_required
def inquiry_new(request):
    """إنشاء استفسار جديد"""
    if not _is_blind(request.user) and not _is_librarian(request.user):
        messages.error(request, 'ليس لديك صلاحية لإنشاء استفسار.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = InquiryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.created_by = request.user

            # إذا كان النص موجوداً، اعتبره مفرغاً
            if inquiry.question_text.strip():
                inquiry.status = Inquiry.Status.TRANSCRIBED
                inquiry.transcription_text = inquiry.question_text.strip()

            inquiry.save()
            messages.success(request, 'تم إرسال استفسارك بنجاح ✅')
            return redirect('service:inquiry_detail', pk=inquiry.pk)
    else:
        form = InquiryCreateForm()

    return render(request, 'service/inquiry_new.html', {'form': form})


@login_required
def inquiry_detail(request, pk: int):
    """عرض تفاصيل الاستفسار"""
    inquiry = get_object_or_404(
        Inquiry.objects.select_related('created_by', 'answered_by'),
        pk=pk
    )

    # التحقق من الصلاحيات
    is_librarian = _is_librarian(request.user)
    if not is_librarian and inquiry.created_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لعرض هذا الاستفسار.')
        return HttpResponseForbidden()

    # تحديث حالة القراءة
    if is_librarian and not inquiry.is_read_by_librarian:
        inquiry.is_read_by_librarian = True
        inquiry.save(update_fields=['is_read_by_librarian'])
    elif not is_librarian and not inquiry.is_read_by_user and inquiry.status == Inquiry.Status.ANSWERED:
        inquiry.is_read_by_user = True
        inquiry.save(update_fields=['is_read_by_user'])

    context = {
        'inquiry': inquiry,
        'is_librarian': is_librarian,
    }
    return render(request, 'service/inquiry_detail.html', context)


@login_required
def inquiry_transcribe(request, pk: int):
    """تفريغ السؤال الصوتي"""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if not _is_librarian(request.user):
        messages.error(request, 'فقط أخصائيي المكتبة يمكنهم تفريغ الأسئلة.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = TranscribeForm(request.POST, instance=inquiry)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = Inquiry.Status.TRANSCRIBED
            obj.save()
            messages.success(request, 'تم حفظ التفريغ بنجاح ✅')
            return redirect('service:inquiry_detail', pk=pk)
    else:
        form = TranscribeForm(instance=inquiry)

    context = {
        'form': form,
        'inquiry': inquiry,
    }
    return render(request, 'service/inquiry_transcribe.html', context)


@login_required
def inquiry_answer(request, pk: int):
    """الإجابة على الاستفسار"""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if not _is_librarian(request.user):
        messages.error(request, 'فقط أخصائيي المكتبة يمكنهم الإجابة.')
        return HttpResponseForbidden()

    # التحقق من التفريغ
    if inquiry.status == Inquiry.Status.NEW and not inquiry.transcription_text.strip():
        messages.warning(request, 'يرجى تفريغ السؤال الصوتي أولاً.')
        return redirect('service:inquiry_transcribe', pk=pk)

    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=inquiry)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.answered_by = request.user
            obj.answered_at = timezone.now()
            obj.status = Inquiry.Status.ANSWERED
            obj.is_read_by_user = False  # إعادة تعيين للإشعار
            obj.save()
            messages.success(request, 'تم إرسال الإجابة بنجاح ✅')
            return redirect('service:inquiry_detail', pk=pk)
    else:
        form = AnswerForm(instance=inquiry)

    context = {
        'form': form,
        'inquiry': inquiry,
    }
    return render(request, 'service/inquiry_answer.html', context)


@login_required
@require_POST
def inquiry_update_status(request, pk: int):
    """تحديث حالة الاستفسار (AJAX)"""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if not _is_librarian(request.user):
        return JsonResponse({'error': 'غير مصرح'}, status=403)

    new_status = request.POST.get('status')
    if new_status in dict(Inquiry.Status.choices):
        inquiry.status = new_status
        inquiry.save(update_fields=['status', 'updated_at'])
        return JsonResponse({
            'success': True,
            'status': new_status,
            'status_display': inquiry.get_status_display()
        })

    return JsonResponse({'error': 'حالة غير صالحة'}, status=400)


@login_required
def inquiry_close(request, pk: int):
    """إغلاق الاستفسار"""
    inquiry = get_object_or_404(Inquiry, pk=pk)

    if not _is_librarian(request.user) and inquiry.created_by != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        inquiry.status = Inquiry.Status.CLOSED
        inquiry.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'تم إغلاق الاستفسار.')
        return redirect('service:dashboard')

    return render(request, 'service/inquiry_close.html', {'inquiry': inquiry})


# ============================================
# عروض قاموس المصطلحات
# ============================================

def glossary_list(request):
    """عرض قائمة المصطلحات"""
    q = request.GET.get('q', '').strip()

    terms = GlossaryTerm.objects.all()
    if q:
        terms = terms.filter(
            Q(term__icontains=q) | Q(definition__icontains=q)
        )

    # الصفحات
    paginator = Paginator(terms, 20)
    page = request.GET.get('page', 1)
    terms_page = paginator.get_page(page)

    context = {
        'terms': terms_page,
        'q': q,
    }
    return render(request, 'service/glossary_list.html', context)


def glossary_detail(request, pk: int):
    """عرض تفاصيل المصطلح"""
    term = get_object_or_404(GlossaryTerm, pk=pk)

    # زيادة عدد المشاهدات
    term.increment_view()

    return render(request, 'service/glossary_detail.html', {'term': term})


@login_required
def glossary_new(request):
    """إضافة مصطلح جديد"""
    if not _is_librarian(request.user):
        messages.error(request, 'فقط أخصائيي المكتبة يمكنهم إضافة المصطلحات.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = GlossaryTermForm(request.POST)
        if form.is_valid():
            term = form.save(commit=False)
            term.created_by = request.user
            term.save()
            messages.success(request, 'تم إضافة المصطلح بنجاح ✅')
            return redirect('service:glossary_detail', pk=term.pk)
    else:
        form = GlossaryTermForm()

    return render(request, 'service/glossary_new.html', {'form': form})


@login_required
def glossary_edit(request, pk: int):
    """تعديل مصطلح"""
    term = get_object_or_404(GlossaryTerm, pk=pk)

    if not _is_librarian(request.user):
        messages.error(request, 'فقط أخصائيي المكتبة يمكنهم تعديل المصطلحات.')
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = GlossaryTermForm(request.POST, instance=term)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المصطلح بنجاح ✅')
            return redirect('service:glossary_detail', pk=term.pk)
    else:
        form = GlossaryTermForm(instance=term)

    return render(request, 'service/glossary_edit.html', {'form': form, 'term': term})


@login_required
@require_POST
def glossary_delete(request, pk: int):
    """حذف مصطلح"""
    term = get_object_or_404(GlossaryTerm, pk=pk)

    if not _is_librarian(request.user):
        return JsonResponse({'error': 'غير مصرح'}, status=403)

    term_name = term.term
    term.delete()
    messages.success(request, f'تم حذف المصطلح "{term_name}".')
    return redirect('service:glossary_list')


@require_POST
def glossary_tts_played(request, pk: int):
    """تسجيل تشغيل القراءة الصوتية (AJAX)"""
    term = get_object_or_404(GlossaryTerm, pk=pk)
    term.tts_play_count += 1
    term.save(update_fields=['tts_play_count'])
    return JsonResponse({'success': True, 'count': term.tts_play_count})


# ============================================
# عروض تحويل النص إلى كلام (TTS)
# Text-to-Speech Views using XTTS-v2
# ============================================

import json
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from .tts_service import get_tts_service, get_audio_url


@require_POST
def tts_synthesize(request):
    """
    API لتحويل النص العربي إلى كلام

    POST /service/tts/synthesize/
    Content-Type: application/json

    Request:
        {"text": "مرحباً بكم", "voice": "female"}

    Response:
        {"success": true, "audio_url": "/media/tts_audio/tts_female_xxx.wav"}
    """
    try:
        # Parse request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {
                'text': request.POST.get('text', ''),
                'voice': request.POST.get('voice', 'female')
            }

        text = data.get('text', '').strip()
        voice = data.get('voice', 'female')
        speed = data.get('speed', 'normal')

        # Validation
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'النص مطلوب - Text is required'
            }, status=400)

        if voice not in ['male', 'female']:
            voice = 'female'

        if speed not in ['slow', 'normal', 'fast']:
            speed = 'normal'

        if len(text) > 2000:
            return JsonResponse({
                'success': False,
                'error': 'النص طويل جداً (الحد الأقصى 2000 حرف)'
            }, status=400)

        # Generate speech
        tts = get_tts_service()
        audio_path = tts.synthesize(text, voice, speed)
        audio_url = get_audio_url(audio_path)

        return JsonResponse({
            'success': True,
            'audio_url': audio_url,
            'voice': voice,
            'speed': speed,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def tts_stream(request):
    """
    تدفق الصوت مباشرة

    GET /service/tts/stream/?text=مرحباً&voice=female

    Returns: audio/wav
    """
    text = request.GET.get('text', '').strip()
    voice = request.GET.get('voice', 'female')

    if not text:
        return JsonResponse({'error': 'النص مطلوب'}, status=400)

    if len(text) > 500:
        return JsonResponse({'error': 'النص طويل جداً للتدفق المباشر'}, status=400)

    try:
        tts = get_tts_service()
        audio_bytes = tts.synthesize_to_bytes(text, voice)

        response = HttpResponse(audio_bytes, content_type='audio/wav')
        response['Content-Disposition'] = 'inline; filename="speech.wav"'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def tts_voices(request):
    """
    الحصول على قائمة الأصوات المتاحة

    GET /service/tts/voices/
    """
    tts = get_tts_service()
    voices = tts.get_available_voices()
    engine = tts.get_engine_info()
    return JsonResponse({'voices': voices, 'engine': engine})


@login_required
@require_POST
def tts_inquiry_answer(request, pk: int):
    """
    تحويل إجابة الاستفسار إلى كلام

    POST /service/inquiry/<pk>/tts/
    """
    inquiry = get_object_or_404(Inquiry, pk=pk)
    voice = request.POST.get('voice', 'female')

    # التحقق من الصلاحيات
    is_librarian = _is_librarian(request.user)
    if not is_librarian and inquiry.created_by != request.user:
        return JsonResponse({
            'success': False,
            'error': 'غير مصرح'
        }, status=403)

    if not inquiry.answer_text:
        return JsonResponse({
            'success': False,
            'error': 'لا توجد إجابة لقراءتها'
        }, status=400)

    try:
        tts = get_tts_service()
        audio_path = tts.synthesize(inquiry.answer_text, voice)
        audio_url = get_audio_url(audio_path)

        return JsonResponse({
            'success': True,
            'audio_url': audio_url
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
def tts_glossary_term(request, pk: int):
    """
    تحويل مصطلح من القاموس إلى كلام

    POST /service/glossary/<pk>/tts/

    Parameters:
        type: 'term' | 'definition' | 'full'
        voice: 'male' | 'female'
    """
    term = get_object_or_404(GlossaryTerm, pk=pk)

    # Accept both JSON body and form data
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = {}
    voice = data.get('voice') or request.POST.get('voice', 'female')
    content_type = data.get('mode') or data.get('type') or request.POST.get('type', 'full')

    # Build text based on type
    if content_type == 'term':
        text = term.term
    elif content_type == 'definition':
        text = term.definition
    else:  # full
        text = f"{term.term}. {term.definition}"

    try:
        tts = get_tts_service()
        audio_path = tts.synthesize(text, voice)
        audio_url = get_audio_url(audio_path)

        # Update TTS play count
        term.tts_play_count = (term.tts_play_count or 0) + 1
        term.save(update_fields=['tts_play_count'])

        return JsonResponse({
            'success': True,
            'audio_url': audio_url,
            'play_count': term.tts_play_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
