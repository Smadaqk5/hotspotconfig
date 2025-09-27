from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reports_dashboard(request):
    """Display reports dashboard"""
    return render(request, 'reports/dashboard.html', {
        'user': request.user,
        'page_title': 'Reports'
    })
