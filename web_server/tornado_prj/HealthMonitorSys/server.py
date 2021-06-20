from tornado import web
import tornado
from peewee_async import Manager
from concurrent.futures import ThreadPoolExecutor

from HealthMonitor.urls import urlpattern
from HealthMonitor.settings import settings, database
from apps.ECG.handlers import EcgDataMonitor, DataMonitor

executor = ThreadPoolExecutor(max_workers=20)

if __name__ == "__main__":
    # 集成json到wtforms
    import wtforms_json

    wtforms_json.init()

    app = web.Application(urlpattern, debug=True, **settings)
    app.listen(8008,address="0.0.0.0")

    objects = Manager(database)
    # No need for sync anymore!
    database.set_allow_sync(False)
    app.objects = objects

    loop = tornado.ioloop.IOLoop.current()
    msg_callback = EcgDataMonitor.EcgRealTimeHandler.send_message
    # msg_callback = EcgDataMonitor.EcgRealTimeHandler.th_send_message
    #
    # # run `read_from_serial` in another thread
    # executor.submit(loop)
    executor.submit(EcgDataMonitor.read_from_serial, loop, msg_callback)
    # executor.submit(DataMonitor.RealTimeHandler.thread_send_message)
    # tornado.ioloop.IOLoop.current().start()
    loop.start()

# self.redirect方法和RedirectHandler方法区别是什么
# self.redirect
