# Import mọi model cần thiết từ các file khác
from .user_activity import UserActivityLog
from .base import *
from .discount import *
from .subscription import *
from .warranty import *
from .source import Source, SourceProduct, SourceLog
from .product import Product
from .system_notification import SystemNotification
from .warranty import WarrantyHistory, WarrantyRequest, WarrantyReason, WarrantyService, WarrantyRequestHistory
from .event import Event
from .conversation import ChatbotConversation
from .source_history import SourceHistory
# Import từ module cha cho các model chỉ được định nghĩa trong file models.py
from .. import models as dashboard_models
# Import các model khác nếu cần

__all__ = [
    'Event', 'ChatbotConversation',
    'WarrantyRequest', 'WarrantyReason', 'WarrantyService', 
    'WarrantyHistory', 'WarrantyRequestHistory',
    'Source', 'SourceProduct', 'SourceLog', 'SourceHistory',
]