from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TermForm
from service.models import GlossaryTerm as Term


def term_list(request):
    q = (request.GET.get('q') or '').strip()
    terms = Term.objects.all().order_by('term')
    if q:
        terms = terms.filter(term__icontains=q)
    return render(request, 'glossary/list.html', {'terms': terms, 'q': q})


def term_detail(request, pk: int):
    term = get_object_or_404(Term, pk=pk)
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
