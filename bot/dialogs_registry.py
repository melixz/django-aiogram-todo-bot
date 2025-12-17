from aiogram import Dispatcher
from dialogs.main_menu import main_menu_dialog
from dialogs.tasks import create_task_dialog, task_list_dialog


def register_dialogs(dp: Dispatcher):
    dp.include_router(main_menu_dialog)
    dp.include_router(task_list_dialog)
    dp.include_router(create_task_dialog)
