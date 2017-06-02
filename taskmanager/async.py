import psycopg2
from multiprocessing import Process
from datetime import datetime
from system.settings import MAX_TASKS_LEN
from .simpletimer import countdown
from .models import Task


def worker(task_id):
    """
    Асинхронный запуск счетчика. Обновляет состояние задачи с переданным id, по завершению
    удаляет id задачи из списка исполняемых.
    """
    db_conn = psycopg2.connect(host='localhost', user='web_user', password='123', database='dr_web')
    cur = db_conn.cursor()
    cur.execute("UPDATE taskmanager_task SET status = '{0}' WHERE id={1}".format(Task.RUN, task_id))
    db_conn.commit()
    countdown()
    cur.execute("UPDATE taskmanager_task SET status = '{0}' WHERE id={1}".format(Task.FINISHED, task_id))
    db_conn.commit()
    cur.execute("SELECT task_exec FROM taskmanager_queue WHERE status_queue='WR'")
    task_exec = cur.fetchall()[0][0]
    task_exec.remove(task_id)
    cur.execute("UPDATE taskmanager_queue SET task_exec = '{" + str(task_exec)[1:-1] + "}' WHERE status_queue='WR'")
    cur.execute(
        "UPDATE taskmanager_task SET finish_time = '{0}' WHERE id={1}".format(
            datetime.now().time().isoformat(), task_id
        )
    )
    db_conn.commit()
    db_conn.close()


def amqp_equivalent():
    """
    Асинхронная очередь задач. Выбирает id задач из списка task_queue до полного его исчерпания.
    Запускается, если пустая очередь заданий (список task_queue) получает id задачи.
    Так как количество одновременно выполняемых задач ограниченно, ведется проверка списка испольняемых
    в данный момент задач task_exec.
    """
    while True:
        db_conn = psycopg2.connect(host='localhost', user='web_user', password='123', database='dr_web')
        cur = db_conn.cursor()
        cur.execute("SELECT task_queue, task_exec FROM taskmanager_queue WHERE status_queue='WR'")
        task_queue, task_exec = cur.fetchall()[0]
        if len(task_queue) == 0:
            db_conn.close()
            break
        if len(task_exec) < MAX_TASKS_LEN:
            task_id = task_queue.pop(0)
            task_exec.append(task_id)
            cur.execute(
                "UPDATE taskmanager_queue SET task_queue = '{"+str(task_queue)[1:-1] + "}' WHERE status_queue='WR'"
            )
            cur.execute(
                "UPDATE taskmanager_queue SET task_exec = '{"+str(task_exec)[1:-1] + "}' WHERE status_queue='WR'"
            )
            db_conn.commit()
            counter = Process(target=worker, args=(task_id,))
            counter.start()
        db_conn.close()
