from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Set up periodic tasks for checking due tasks"

    def handle(self, *args, **options):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Created interval schedule: every 1 minute"))

        task, created = PeriodicTask.objects.update_or_create(
            name="Check due tasks",
            defaults={
                "interval": schedule,
                "task": "tasks.tasks.check_due_tasks",
                "enabled": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Created periodic task: Check due tasks"))
        else:
            self.stdout.write(self.style.SUCCESS("Updated periodic task: Check due tasks"))

        self.stdout.write(self.style.SUCCESS("Periodic tasks setup completed!"))
