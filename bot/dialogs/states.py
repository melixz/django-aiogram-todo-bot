from aiogram.fsm.state import State, StatesGroup


class MainMenuSG(StatesGroup):
    main = State()


class TaskListSG(StatesGroup):
    list = State()
    detail = State()


class CreateTaskSG(StatesGroup):
    title = State()
    description = State()
    category = State()
    input_category_name = State()  # Новое состояние
    due_date = State()
    confirm = State()
