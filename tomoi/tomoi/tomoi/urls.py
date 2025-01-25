from django.urls import path, include

urlpatterns = [
    # ... các URL khác
    path('accounts/', include('accounts.urls', namespace='accounts')),
] 