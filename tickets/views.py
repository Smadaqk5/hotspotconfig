from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def tickets_list(request):
    """Display list of tickets"""
    return render(request, 'tickets/list.html', {
        'user': request.user,
        'page_title': 'Tickets'
    })

@login_required
def tickets_generate(request):
    """Generate new tickets"""
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'tickets/generate.html', {
        'user': request.user,
        'page_title': 'Generate Tickets'
    })