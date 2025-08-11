import flet as ft
from utils.i18n_service import Translator

class LanguageSelector(ft.UserControl):
    def __init__(self, page: ft.Page, translator: Translator):
        super().__init__()
        self.page = page
        self.translator = translator

    def build(self):
        # Create dropdown options from the languages loaded by the translator
        dropdown_options = []
        for lang_code in self.translator.languages.keys():
            # You could have a mapping for full language names, e.g., {"es": "Español"}
            dropdown_options.append(ft.dropdown.Option(lang_code, lang_code.upper()))

        return ft.Dropdown(
            value=self.translator.current_lang,
            options=dropdown_options,
            on_change=self.language_changed,
            width=100,
            border_width=0, # Make it look clean in the AppBar
        )

    def language_changed(self, e):
        """
        Called when the user selects a new language from the dropdown.
        """
        selected_lang = e.control.value
        # The set_language method handles updating the session and the page
        self.translator.set_language(self.page, selected_lang)
        # We need to force a re-render of the entire view to see the changes
        self.page.go(self.page.route)
