from django.conf.urls import url
from .views import CheckTaskStatusAPI, CreateNewTaskAPI, StatusTaskFront, AddButtonFront

urlpatterns = [
    url(r'^task_status/$', CheckTaskStatusAPI.as_view(), name="task_status"),
    url(r'^task_add/$', CreateNewTaskAPI.as_view(), name="task_add"),
    url(r'^status/$', StatusTaskFront.as_view(), name="status_page"),
    url(r'^$', AddButtonFront.as_view(), name="create_page"),
]
