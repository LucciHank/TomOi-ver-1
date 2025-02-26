from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):
    """
    Template tag dùng cho phân trang để giữ lại các tham số GET khi chuyển trang
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode() 