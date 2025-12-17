from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from dialogs.states import CreateTaskSG, MainMenuSG, TaskListSG


async def cmd_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuSG.main, mode=StartMode.RESET_STACK)


async def cmd_tasks(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskListSG.list, mode=StartMode.RESET_STACK)


async def cmd_new(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(CreateTaskSG.title, mode=StartMode.RESET_STACK)


def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_tasks, Command("tasks"))
    dp.message.register(cmd_new, Command("new"))
