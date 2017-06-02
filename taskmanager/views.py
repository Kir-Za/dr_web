from multiprocessing import Process
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from datetime import datetime
from .async import amqp_equivalent
from .models import Task, Queue


class CheckTaskStatusAPI(View):
    """
    Запрос состояния существующих задач.
    """
    def get(self, request):
        common_tasks_query = Task.objects.all().order_by('-create_time')
        tasks_list = []
        for element in common_tasks_query:
            tmp_dict = {
                "id": element.id,
                "status": element.status,
                "create_time": element.create_time.strftime('%H:%M:%S')
            }
            if element.status == Task.FINISHED:
                tmp_dict.update({"finish_time": element.finish_time.strftime('%H:%M:%S')})
            else:
                tmp_dict.update({"finish_time": "Unknown"})
            tasks_list.append(tmp_dict)
        return JsonResponse({"result": tasks_list})


class CreateNewTaskAPI(View):
    """
    Создание новой записи задачи в базе.
    Постановка новой задачи в очередь на выполнение.
    """
    def get(self, request):
        new_task = Task.objects.create(create_time=datetime.now().time())
        tasks, result = Queue.objects.get_or_create(status_queue='WR')
        tasks.task_queue.append(new_task.id)
        tasks.save()
        if len(tasks.task_queue) == 1:
            tmp_proc = Process(target=amqp_equivalent, args=())
            tmp_proc.start()
        return JsonResponse({"resutl": 200})


class StatusTaskFront(TemplateView):
    """
    Имитация JS фронт приложения.
    Отображает состояние заданий.
    """
    template_name = 'task_status.html'


class AddButtonFront(TemplateView):
    """
    Имитация JS фронт приложения.
    Дбавление новых заданий.
    """
    template_name = 'task_add.html'
