from django.shortcuts import render, redirect

def discount_list(request):
    return render(request, 'dashboard/discounts/list.html')

def discount_add(request):
    return render(request, 'dashboard/discounts/form.html')

def discount_edit(request, discount_id):
    return render(request, 'dashboard/discounts/form.html')

def discount_delete(request, discount_id):
    return redirect('dashboard:discounts')

# Thêm các view khác...
