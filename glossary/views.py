from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import TermForm
from service.models import GlossaryCategory, GlossaryTerm as Term


@ensure_csrf_cookie
def term_list(request):
    q = (request.GET.get('q') or '').strip()
    cat_id = request.GET.get('category', '').strip()

    terms = Term.objects.select_related('category').all().order_by('term')
    if q:
        terms = terms.filter(term__icontains=q)
    if cat_id:
        terms = terms.filter(category_id=cat_id)

    categories = GlossaryCategory.objects.annotate(
        num_terms=Count('terms')
    ).order_by('order', 'name')

    return render(request, 'glossary/list.html', {
        'terms': terms,
        'q': q,
        'categories': categories,
        'selected_category': cat_id,
    })


@ensure_csrf_cookie
def term_detail(request, pk: int):
    term = get_object_or_404(Term.objects.select_related('category'), pk=pk)
    term.increment_view()
    return render(request, 'glossary/detail.html', {'term': term})


@login_required
def term_new(request):
    if not getattr(request.user, 'is_librarian', lambda: False)():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = TermForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'تمت إضافة المصطلح')
            return redirect('glossary:detail', pk=obj.pk)
    else:
        form = TermForm()

    return render(request, 'glossary/new.html', {'form': form})
