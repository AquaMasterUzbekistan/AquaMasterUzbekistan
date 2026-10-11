from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.navigation import back_home_row, pagination_row, build_list_keyboard
from app.keyboards.common import confirm_cancel_keyboard, yes_no_keyboard
from app.keyboards.african import african_menu_keyboard, malawi_menu_keyboard, tanganyika_menu_keyboard
from app.keyboards.american import american_menu_keyboard
from app.keyboards.discus import discus_menu_keyboard
from app.keyboards.other_fish import other_fish_menu_keyboard
from app.keyboards.profile import profile_tabs_keyboard
from app.keyboards.search import calculators_menu_keyboard, search_results_keyboard
from app.keyboards.admin import admin_menu_keyboard

__all__ = [
    "main_menu_keyboard", "back_home_row", "pagination_row", "build_list_keyboard",
    "confirm_cancel_keyboard", "yes_no_keyboard",
    "african_menu_keyboard", "malawi_menu_keyboard", "tanganyika_menu_keyboard",
    "american_menu_keyboard", "discus_menu_keyboard", "other_fish_menu_keyboard",
    "profile_tabs_keyboard",
    "calculators_menu_keyboard", "search_results_keyboard",
    "admin_menu_keyboard",
]
