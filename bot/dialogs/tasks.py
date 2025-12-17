from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Column,
    Row,
    Select,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from api_client import get_api_client

from dialogs.states import CreateTaskSG, TaskListSG


async def get_tasks_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    telegram_id = dialog_manager.event.from_user.id
    client = get_api_client(telegram_id)

    try:
        tasks = await client.get_tasks()
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        tasks.sort(key=lambda x: x.get("is_completed", False), reverse=False)
        tasks = tasks[:10]
    except Exception as e:
        tasks = []
        dialog_manager.dialog_data["error"] = str(e)
    finally:
        await client.close()

    for task in tasks:
        task["status_icon"] = "✅" if task.get("is_completed") else "⏳"

    return {
        "tasks": tasks,
        "has_tasks": len(tasks) > 0,
        "task_count": len(tasks),
    }


async def on_task_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str,
):
    telegram_id = callback.from_user.id
    client = get_api_client(telegram_id)

    try:
        task = await client.get_task(item_id)
        dialog_manager.dialog_data["selected_task"] = task
        await dialog_manager.switch_to(TaskListSG.detail)
    except Exception as e:
        await callback.answer(f"Ошибка при загрузке задачи: {e}")
    finally:
        await client.close()


async def get_task_detail_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    task = dialog_manager.dialog_data.get("selected_task", {})
    if not task:
        return {}

    created_at = task.get("created_at", "")
    if created_at:
        from datetime import datetime

        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            created_at = dt.strftime("%d.%m.%Y %H:%M")
        except (ValueError, AttributeError):
            pass

    due_date = task.get("due_date", "")
    if due_date:
        from datetime import datetime

        try:
            dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            due_date = dt.strftime("%d.%m.%Y %H:%M")
        except (ValueError, AttributeError):
            pass

    category = task.get("category")
    category_name = category.get("name") if category else "Без категории"

    is_completed = task.get("is_completed", False)
    status_text = "Выполнена" if is_completed else "В процессе"
    status_emoji = "✅" if is_completed else "⏳"

    return {
        "title": task.get("title", ""),
        "description": task.get("description", "") or "Нет описания",
        "category_name": category_name,
        "due_date": due_date or "Не указан",
        "created_at": created_at,
        "is_completed": is_completed,
        "status_emoji": status_emoji,
        "status_text": status_text,
    }


async def on_complete_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    task = dialog_manager.dialog_data.get("selected_task", {})
    task_id = task.get("id")

    if not task_id:
        await callback.answer("Задача не найдена")
        return

    telegram_id = callback.from_user.id
    client = get_api_client(telegram_id)

    try:
        updated_task = await client.complete_task(task_id)
        dialog_manager.dialog_data["selected_task"] = updated_task
        await callback.answer("✅ Задача выполнена!")
        # Обновляем данные окна
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
    finally:
        await client.close()


async def on_delete_task(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    task = dialog_manager.dialog_data.get("selected_task", {})
    task_id = task.get("id")

    if not task_id:
        await callback.answer("Задача не найдена")
        return

    telegram_id = callback.from_user.id
    client = get_api_client(telegram_id)

    try:
        await client.delete_task(task_id)
        await callback.answer("🗑 Задача удалена!")
        await dialog_manager.switch_to(TaskListSG.list)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
    finally:
        await client.close()


task_list_dialog = Dialog(
    Window(
        Const("📋 <b>Мои задачи</b>\n"),
        Format("Всего задач: {task_count}\n", when="has_tasks"),
        Const("У вас пока нет задач.", when=lambda data, *args: not data.get("has_tasks")),
        Column(
            Select(
                Format("{item[status_icon]} {item[title]}"),
                id="task_select",
                item_id_getter=lambda item: item["id"],
                items="tasks",
                on_click=on_task_selected,
            ),
        ),
        Row(
            Start(
                Const("➕ Новая задача"),
                id="new_task",
                state=CreateTaskSG.title,
            ),
            Cancel(Const("🔙 Назад")),
        ),
        state=TaskListSG.list,
        getter=get_tasks_data,
    ),
    Window(
        Format("<b>{title}</b>\n"),
        Format("{status_emoji} Статус: {status_text}\n"),
        Format("📁 Категория: {category_name}\n"),
        Format("📅 Срок: {due_date}\n"),
        Format("🕐 Создана: {created_at}\n\n"),
        Format("📝 {description}"),
        Row(
            Button(
                Const("✅ Выполнить"),
                id="complete",
                on_click=on_complete_task,
                when=lambda data, *args: not data.get("is_completed"),
            ),
            Button(
                Const("🗑 Удалить"),
                id="delete",
                on_click=on_delete_task,
            ),
        ),
        SwitchTo(Const("🔙 К списку"), id="back_to_list", state=TaskListSG.list),
        state=TaskListSG.detail,
        getter=get_task_detail_data,
    ),
)


async def on_title_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["title"] = message.text
    await dialog_manager.switch_to(CreateTaskSG.description)


async def on_description_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["description"] = message.text
    await dialog_manager.switch_to(CreateTaskSG.category)


async def on_skip_description(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["description"] = ""
    await dialog_manager.switch_to(CreateTaskSG.category)


async def get_categories_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    telegram_id = dialog_manager.event.from_user.id
    client = get_api_client(telegram_id)

    try:
        categories = await client.get_categories()
    except Exception:
        categories = []
    finally:
        await client.close()

    return {
        "categories": categories,
        "has_categories": len(categories) > 0,
    }


async def on_category_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data["category_id"] = item_id

    categories = await get_categories_data(dialog_manager)
    for cat in categories.get("categories", []):
        if cat["id"] == item_id:
            dialog_manager.dialog_data["category_name"] = cat["name"]
            break

    await dialog_manager.switch_to(CreateTaskSG.due_date)


async def on_skip_category(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["category_id"] = None
    dialog_manager.dialog_data["category_name"] = "Без категории"
    await dialog_manager.switch_to(CreateTaskSG.due_date)


async def on_new_category_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    name = message.text.strip()
    telegram_id = message.from_user.id
    client = get_api_client(telegram_id)

    try:
        category = await client.create_category(name)
        dialog_manager.dialog_data["category_id"] = category["id"]
        dialog_manager.dialog_data["category_name"] = category["name"]
        await message.answer(f"✅ Категория '{name}' создана и выбрана.")
        await dialog_manager.switch_to(CreateTaskSG.due_date)
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании категории: {e}")
    finally:
        await client.close()


async def on_due_date_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    from datetime import datetime

    text = message.text.strip()

    formats = [
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ]

    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue

    if parsed_date is None:
        await message.answer(
            "❌ Неверный формат даты. Используйте: ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ"
        )
        return

    dialog_manager.dialog_data["due_date"] = parsed_date.isoformat()
    dialog_manager.dialog_data["due_date_display"] = text
    await dialog_manager.switch_to(CreateTaskSG.confirm)


async def on_skip_due_date(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["due_date"] = None
    dialog_manager.dialog_data["due_date_display"] = "Не указан"
    await dialog_manager.switch_to(CreateTaskSG.confirm)


async def get_confirm_data(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    data = dialog_manager.dialog_data
    return {
        "title": data.get("title", ""),
        "description": data.get("description", "") or "Нет описания",
        "category_name": data.get("category_name", "Без категории"),
        "due_date": data.get("due_date_display", "Не указан"),
    }


async def on_confirm_create(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    data = dialog_manager.dialog_data
    telegram_id = callback.from_user.id
    client = get_api_client(telegram_id)

    try:
        await client.create_task(
            title=data.get("title", ""),
            description=data.get("description", ""),
            category_id=data.get("category_id"),
            due_date=data.get("due_date"),
        )
        await callback.answer("✅ Задача создана!")
        await dialog_manager.done()
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
    finally:
        await client.close()


create_task_dialog = Dialog(
    Window(
        Const("➕ <b>Новая задача</b>\n\n"),
        Const("📝 Введите название задачи:"),
        MessageInput(on_title_input),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskSG.title,
    ),
    Window(
        Const("📝 <b>Описание</b>\n\n"),
        Const("Введите описание задачи (или пропустите):"),
        MessageInput(on_description_input),
        Button(Const("⏭ Пропустить"), id="skip_desc", on_click=on_skip_description),
        Back(Const("🔙 Назад")),
        state=CreateTaskSG.description,
    ),
    Window(
        Const("📁 <b>Категория</b>\n\n"),
        Const("Выберите категорию:", when="has_categories"),
        Const(
            "У вас нет категорий. Создайте новую или пропустите.",
            when=lambda data, *args: not data.get("has_categories"),
        ),
        Column(
            Select(
                Format("{item[name]}"),
                id="category_select",
                item_id_getter=lambda item: item["id"],
                items="categories",
                on_click=on_category_selected,
            ),
            when="has_categories",
        ),
        SwitchTo(
            Const("➕ Создать новую"),
            id="create_new_cat",
            state=CreateTaskSG.input_category_name,
        ),
        Button(Const("⏭ Без категории"), id="skip_cat", on_click=on_skip_category),
        Back(Const("🔙 Назад")),
        state=CreateTaskSG.category,
        getter=get_categories_data,
    ),
    Window(
        Const("📁 <b>Новая категория</b>\n\n"),
        Const("Введите название новой категории:"),
        MessageInput(on_new_category_input),
        SwitchTo(Const("🔙 Назад к выбору"), id="back_to_cat_select", state=CreateTaskSG.category),
        state=CreateTaskSG.input_category_name,
    ),
    Window(
        Const("📅 <b>Срок выполнения</b>\n\n"),
        Const("Введите дату и время (ДД.ММ.ГГГГ ЧЧ:ММ)\nили пропустите:"),
        MessageInput(on_due_date_input),
        Button(Const("⏭ Пропустить"), id="skip_due", on_click=on_skip_due_date),
        SwitchTo(Const("🔙 Назад"), id="back_to_cat_from_date", state=CreateTaskSG.category),
        state=CreateTaskSG.due_date,
    ),
    Window(
        Const("✅ <b>Подтверждение</b>\n\n"),
        Format("📌 <b>{title}</b>\n"),
        Format("📝 {description}\n"),
        Format("📁 Категория: {category_name}\n"),
        Format("📅 Срок: {due_date}\n\n"),
        Const("Создать задачу?"),
        Row(
            Button(Const("✅ Создать"), id="confirm", on_click=on_confirm_create),
            Cancel(Const("❌ Отмена")),
        ),
        SwitchTo(Const("🔙 Назад"), id="back_to_date", state=CreateTaskSG.due_date),
        state=CreateTaskSG.confirm,
        getter=get_confirm_data,
    ),
)
