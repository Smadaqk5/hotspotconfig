"""
Captive Portal views for end users
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json

from tickets.models import Ticket, TicketUsage
from accounts.models import Provider


def portal_login(request, provider_id=None):
    """Main captive portal login page"""
    provider = None
    if provider_id:
        provider = get_object_or_404(Provider, id=provider_id)
    
    context = {
        'provider': provider,
        'page_title': 'WiFi Access Portal'
    }
    return render(request, 'captive_portal/login.html', context)


@csrf_exempt
def validate_ticket(request):
    """Validate ticket code and grant access"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_code = data.get('ticket_code', '').strip().upper()
            provider_id = data.get('provider_id')
            
            if not ticket_code:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a ticket code'
                })
            
            # Find the ticket
            ticket_query = Ticket.objects.filter(code=ticket_code)
            if provider_id:
                ticket_query = ticket_query.filter(provider_id=provider_id)
            
            try:
                ticket = ticket_query.get()
            except Ticket.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid ticket code'
                })
            
            # Check if ticket is valid
            if not ticket.can_use():
                if ticket.is_expired():
                    return JsonResponse({
                        'success': False,
                        'message': 'Ticket has expired'
                    })
                elif ticket.is_used():
                    return JsonResponse({
                        'success': False,
                        'message': 'Ticket has already been used'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Ticket is not active'
                    })
            
            # Create usage tracking
            usage, created = TicketUsage.objects.get_or_create(
                ticket=ticket,
                defaults={
                    'session_start': timezone.now(),
                    'ip_address': get_client_ip(request)
                }
            )
            
            # Mark ticket as used
            ticket.status = 'used'
            ticket.used_at = timezone.now()
            ticket.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Access granted!',
                'ticket': {
                    'code': ticket.code,
                    'type': ticket.ticket_type.name,
                    'value': ticket.ticket_type.value,
                    'expires_at': ticket.expires_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def portal_success(request, ticket_code):
    """Success page after ticket validation"""
    try:
        ticket = Ticket.objects.get(code=ticket_code)
        context = {
            'ticket': ticket,
            'provider': ticket.provider,
            'page_title': 'Access Granted'
        }
        return render(request, 'captive_portal/success.html', context)
    except Ticket.DoesNotExist:
        return render(request, 'captive_portal/error.html', {
            'message': 'Ticket not found',
            'page_title': 'Error'
        })


def portal_error(request):
    """Error page for invalid tickets"""
    message = request.GET.get('message', 'Access denied')
    context = {
        'message': message,
        'page_title': 'Access Denied'
    }
    return render(request, 'captive_portal/error.html', context)
