from django.shortcuts import render, redirect

def banner_list(request):
    return render(request, 'dashboard/banners/list.html')

def banner_add(request):
    return render(request, 'dashboard/banners/form.html')

def banner_edit(request, banner_id):
    return render(request, 'dashboard/banners/form.html')

def banner_delete(request, banner_id):
    return redirect('dashboard:banners')

# Thêm các view khác...
