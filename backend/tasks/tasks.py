import logging

import httpx
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_due_tasks():
    from tasks.models import Task

    now = timezone.now()

    due_tasks = Task.objects.filter(
        due_date__lte=now,
        is_completed=False,
        notification_sent=False,
    ).select_related("category")

    if not due_tasks.exists():
        logger.info("No due tasks found")
        return "No due tasks"

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return "Bot token not configured"

    sent_count = 0
    for task in due_tasks:
        try:
            send_task_notification(task, bot_token)
            task.notification_sent = True
            task.save(update_fields=["notification_sent"])
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send notification for task {task.id}: {e}")

    logger.info(f"Sent {sent_count} notifications")
    return f"Sent {sent_count} notifications"


def send_task_notification(task, bot_token: str):
    category_text = f"\n📁 Категория: {task.category.name}" if task.category else ""
    due_text = task.due_date.strftime("%d.%m.%Y %H:%M") if task.due_date else "Не указана"

    message = (
        f"⏰ <b>Напоминание о задаче!</b>\n\n"
        f"📌 <b>{task.title}</b>\n"
        f"{category_text}\n"
        f"📅 Срок: {due_text}\n\n"
        f"{'📝 ' + task.description if task.description else ''}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": task.telegram_id,
        "text": message,
        "parse_mode": "HTML",
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, timeout=10)
        response.raise_for_status()

    logger.info(f"Sent notification for task {task.id} to user {task.telegram_id}")


@shared_task
def send_immediate_notification(task_id: str):
    from tasks.models import Task

    try:
        task = Task.objects.select_related("category").get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return f"Task {task_id} not found"

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return "Bot token not configured"

    try:
        send_task_notification(task, bot_token)
        task.notification_sent = True
        task.save(update_fields=["notification_sent"])
        return f"Notification sent for task {task_id}"
    except Exception as e:
        logger.error(f"Failed to send notification for task {task_id}: {e}")
        return f"Failed: {e}"
