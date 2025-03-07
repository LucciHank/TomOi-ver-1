from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def settings_view(request):
    return render(request, 'dashboard/settings/index.html') 