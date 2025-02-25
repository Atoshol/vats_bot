from db.models.admin import AdminCRUD
from db.models.client import ClientCRUD
from db.models.message import MessageCRUD, MessageLastIndexCRUD
from db.models.token import TokenPairCRUD, TokenLinkCRUD
from db.models.user import UserCRUD
from db.models.user_settings import UserSettingsCRUD
from db.models.default import SettingsCRUD
from db.models.user_token_log import UserTokenNotificationsCRUD


class DB:
    tokenPair_crud = TokenPairCRUD()
    tokenLink_crud = TokenLinkCRUD()

    admin_crud = AdminCRUD()
    user_crud = UserCRUD()
    user_settings_crud = UserSettingsCRUD()

    message_crud = MessageCRUD()
    messageIndex_crud = MessageLastIndexCRUD()
    client_crud = ClientCRUD()
    default_settings_crud = SettingsCRUD()
    user_token_notifications = UserTokenNotificationsCRUD()
