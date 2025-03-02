from django.contrib import admin
from . import models

# Import tường minh các models cần đăng ký
from .models.base import (
    ChatSession, ChatMessage, SupportTicket, TicketReply,
    EmailTemplate, EmailLog, ReferralProgram, ReferralCode
)
from .models.discount import Discount, UserDiscount, DiscountUsage
from .models.subscription import SubscriptionPlan, UserSubscription, SubscriptionTransaction
from .models.warranty import WarrantyTicket, WarrantyHistory

# Đăng ký models
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(SupportTicket)
admin.site.register(TicketReply)
admin.site.register(EmailTemplate)
admin.site.register(EmailLog)
admin.site.register(Discount)
admin.site.register(UserDiscount)
admin.site.register(DiscountUsage)
admin.site.register(ReferralProgram)
admin.site.register(ReferralCode)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(SubscriptionTransaction)
admin.site.register(WarrantyTicket)
admin.site.register(WarrantyHistory) 