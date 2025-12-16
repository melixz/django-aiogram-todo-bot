from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from dialogs.states import CreateTaskSG, MainMenuSG, TaskListSG

main_menu_dialog = Dialog(
    Window(
        Const("🗂 <b>ToDo Bot</b>\n\n"),
        Const("Выберите действие:"),
        Start(
            Const("📋 Мои задачи"),
            id="tasks",
            state=TaskListSG.list,
        ),
        Start(
            Const("➕ Новая задача"),
            id="new_task",
            state=CreateTaskSG.title,
        ),
        state=MainMenuSG.main,
    ),
)
