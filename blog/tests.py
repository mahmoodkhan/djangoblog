from django.core.urlresolvers import resolve, reverse
from django.template.loader import render_to_string
from django.test import TestCase
from django.test import RequestFactory
from .views import HomeView, BlogPostCreateView

# Create your tests here.
class HomePageTest(TestCase):

    home_page_url = '/'
    new_blogpost_url = '/newpost/'
    def test_root_url_resolves_to_home_page_view(self):
        
        found = resolve(self.home_page_url)
        self.assertEqual(found.view_name, 'home')
        
        request = RequestFactory().get(self.home_page_url)
        view = HomeView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'blog/index.html')
        self.assertEqual(response.template_name, ['blog/index.html', 'blog/blogpost_list.html'])
        code = """
        <code class="python">
            @register.filter(name='cut')
            def cut(value, arg):
                return value.replace(arg, '')

            @register.filter
            def lower(value):
                return value.lower()
        </code>
        """
        self.assertEqual(response.context_data['code'], code)
        self.assertTrue(response.render().content.startswith(b'\n<!DOCTYPE html>'))
        self.assertIn(b'<title>Home</title>', response.render().content)
        self.assertTrue(response.render().content.strip().endswith(b'</html>'))

    def test_home_page_returns_correct_html(self):
        request = RequestFactory().get(self.home_page_url)
        view = HomeView.as_view()
        response = view(request)
        expected_html = render_to_string('blog/index.html')

        # decode converts the response.content bytes into a Python unicode string
        self.assertEqual(response.render().content.decode(), expected_html)

    def test_blogpost_create_view_can_save_POST_request(self):
        params = {
            'title': 'Test Entry', 
            'content': 'This is a test entry', 
            'published': True, 
            'pub_date': '2014-11-21 10:22:00', 
            'category': 1, 
            'tags': 1, 
            'form-0-user': '',
            'form-0-share': '',
            'attachments-TOTAL_FORMS': 2,
            'attachments-INITIAL_FORMS': 0,
            'attachments-MIN_NUM_FORMS': 0,
            'attachments-MAX_NUM_FORMS': 10,
            
        }
        request = RequestFactory().post(self.new_blogpost_url, data = params)
        response = BlogPostCreateView.as_view()(request)
        self.assertIn('Test Entry', response.content.decode())