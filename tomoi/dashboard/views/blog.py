from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_post_category(request):
    """Xóa danh mục bài viết"""
    category_id = request.POST.get('category_id')
    
    # Thực hiện xóa danh mục
    # PostCategory.objects.filter(id=category_id).delete()
    
    return redirect('dashboard:post_categories') 