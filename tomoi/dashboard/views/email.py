from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@login_required
def create_email_template(request):
    """Tạo mẫu email mới"""
    if request.method == 'POST':
        # Xử lý dữ liệu form
        # EmailTemplate.objects.create(
        #     name=request.POST.get('name'),
        #     subject=request.POST.get('subject'),
        #     content=request.POST.get('content'),
        #     created_by=request.user
        # )
        return redirect('dashboard:email_templates')
    
    context = {'title': 'Tạo mẫu email'}
    return render(request, 'dashboard/email/template_form.html', context)

@staff_member_required
@login_required
def edit_email_template(request, template_id):
    """Chỉnh sửa mẫu email"""
    # template = get_object_or_404(EmailTemplate, id=template_id)
    
    if request.method == 'POST':
        # Xử lý dữ liệu form
        # template.name = request.POST.get('name')
        # template.subject = request.POST.get('subject')
        # template.content = request.POST.get('content')
        # template.save()
        return redirect('dashboard:email_templates')
    
    context = {'title': 'Chỉnh sửa mẫu email'}
    return render(request, 'dashboard/email/template_form.html', context) 