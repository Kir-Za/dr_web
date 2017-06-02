from django.db import models
from django.contrib.postgres.fields import ArrayField


class Task(models.Model):
    """
    Задача, выставляемая пользователем
    """
    IN_QUEUE = "Prp"
    RUN = "Run"
    FINISHED = "Fin"
    STATUST_TASK = (
        (IN_QUEUE, 'В очереди'),
        (FINISHED, 'Завершена'),
        (RUN, 'В процессе'),
    )
    create_time = models.TimeField(verbose_name="Время создания задачи")  # auto_now_add требует настройки tz бд
    finish_time = models.TimeField(blank=True, null=True, verbose_name="Время завершения задачи")
    status = models.CharField(
        max_length=3,
        choices=STATUST_TASK,
        default=IN_QUEUE,
        verbose_name="Состояние задачи"
    )


class Queue(models.Model):
    """
    Очередь задач на выполнение.
    """
    WORK_ON = "WR"
    BACKUP = "BU"
    STATUST_QUEUE = (
        (WORK_ON, 'Рабочая/основная'),
        (BACKUP, 'Техническая')
    )
    status_queue = models.CharField(
        max_length=2,
        choices=STATUST_QUEUE,
        default=WORK_ON,
        verbose_name="Статус очереди"
    )
    task_queue = ArrayField(models.PositiveIntegerField(), default=[], verbose_name="Очередь заданий")
    task_exec = ArrayField(models.PositiveIntegerField(), default=[], verbose_name="Исполняемые задания")
