from google.appengine.api import urlfetch
from urllib import urlencode
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
import re

def set_trace():
  import pdb, sys
  debugger = pdb.Pdb(stdin=sys.__stdin__, stdout=sys.__stdout__)
  debugger.set_trace(sys._getframe().f_back)

class SoupToNuts(object):
  """
  A mechanize-inspired screenscraping utility for Google App Engine.

  Public Attributes:
  url -- the current page url
  response -- the raw response from google's urlfetch
  page -- a BeautifulSoup object for the current page
  cookies -- a string representing the current cookies

  Example:
  nuts = SoupToNuts('http://www.google.com')
  puts nuts.page.prettify()
  """

  def __init__(self, url=None):
    """
    Arguments
    url -- an initial url to fetch
    """
    self.url = url
    self.cookies = ''
    if url is not None:
      self.fetch('')

  def submit(self, form, values):
    """
    Submit a form on the page with the passed in values.

    Arguments:
    form -- a BeautifulSoup form element on the page
    values -- a dict of key-value pairs for the form items

    Example:
    nuts.submit(nuts.page.find('form', id='login_form'),
      {'email': 'steve@apple.com', 'password': 'i!<3flash'})
    """
    data = {}
    for i in form('input'):
      attr_names = [a[0] for a in i.attrs]
      if 'name' in attr_names and 'value' in attr_names:
        data[i['name']] = i['value']
    data.update(values)
    return self.fetch(form['action'], data)

  def follow(self, link):
    """
    Follow a link on the page.

    Arguments:
    link -- a BeautifulSoup link element from the page

    Example:
    nuts.follow(nuts.page.a)
    """
    return self.fetch(link['href'])

  def fetch(self, url, data=None, raw=False):
    """
    Fetch a url using Google's urlfetch library.  Does a GET by default
    and a POST if data is supplied.

    Arguments:
    url -- the url to visit, can be a url fragment
    data -- the data to send (via POST)
    raw -- whether to parse the incoming response with BeautifulSoup
    """
    url = urljoin(self.url, url)
    print url

    if data is None:
      method = urlfetch.GET
      payload = None
    else:
      method = urlfetch.POST
      payload = urlencode(data)

    while url is not None:
      self.url = url
      res = urlfetch.fetch(url=url, payload=payload, method=method,
        headers={'Cookie': self.cookies},
        allow_truncated=False, follow_redirects=False,
        deadline=10)
      payload = None
      method = urlfetch.GET
      self.cookies = res.headers.get('set-cookie', '')
      url = res.headers.get('location')

    self.response = res

    if raw:
      self.page = res.content
    else:
      self.page = self.__parse(res.content)
    return self.page

  def __parse(self, html):
    return BeautifulSoup(re.sub('<!.*?>','', html))
