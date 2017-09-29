import os #deploy line: says this is the standard library

import tornado.ioloop
import tornado.web
import tornado.log

from jinja2 import \
  Environment, PackageLoader, select_autoescape

PORT = int(os.environ.get('PORT', '8888')) #deploy line: says get the port variable. If there is no port var, get the default. the default here is 8888. Anything above 1000 works. Ports < 1000 are reserved unless you are a root.

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get(self):
    names = self.get_query_arguments('name')
    self.set_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("base.html", {'names': names, 'amount': 42.55})

class PageHandler(TemplateHandler):
  def get(self, page):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {})

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/page/(.*)", PageHandler),
    (
      r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'static'}
    ),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(PORT, print('Server started on localhost:' + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
