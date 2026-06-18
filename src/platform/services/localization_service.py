"""Small key-based localization service for platform text."""


TRANSLATIONS = {
    "vi": {
        "platform.home.title": "Game Game Go",
        "platform.home.play": "Thư viện game",
        "platform.home.settings": "Cài đặt",
        "platform.home.help": "Giới thiệu",
        "platform.home.quit": "Thoát",
        "platform.library.title": "Thư viện game",
        "platform.library.empty": "Chưa có game khả dụng",
        "platform.settings.title": "Cài đặt",
        "platform.settings.sound": "Âm thanh",
        "platform.settings.volume": "Âm lượng",
        "platform.settings.language": "Ngôn ngữ",
        "common.back": "Quay lại",
        "common.start": "Bắt đầu",
        "common.disabled": "Đang tắt",
    },
    "en": {
        "platform.home.title": "Game Game Go",
        "platform.home.play": "Game Library",
        "platform.home.settings": "Settings",
        "platform.home.help": "About",
        "platform.home.quit": "Quit",
        "platform.library.title": "Game Library",
        "platform.library.empty": "No enabled games",
        "platform.settings.title": "Settings",
        "platform.settings.sound": "Sound",
        "platform.settings.volume": "Volume",
        "platform.settings.language": "Language",
        "common.back": "Back",
        "common.start": "Start",
        "common.disabled": "Disabled",
    },
}


class LocalizationService:
    """Translate platform keys with language and key fallback."""

    def __init__(self, language: str = "vi"):
        self.language = language if language in TRANSLATIONS else "vi"

    def set_language(self, language: str):
        self.language = language if language in TRANSLATIONS else "vi"

    def get(self, key: str) -> str:
        return TRANSLATIONS.get(self.language, {}).get(key) or TRANSLATIONS["en"].get(key) or key

