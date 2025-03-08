from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def google_calendar_auth_temp(request):
    return JsonResponse({'auth_url': '#'})

@login_required
def google_calendar_callback_temp(request):
    return redirect('/dashboard/')

@login_required
def google_calendar_status_temp(request):
    return JsonResponse({
        'is_synced': False,
        'last_sync': 'Chưa đồng bộ'
    }) 