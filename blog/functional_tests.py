from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest, time

class HomePageTests(unittest.TestCase):

    def setUp(self):
        """
        This method is run before tests start
        """
        self.browser = webdriver.Firefox()
        
        # make selenium wait if it needs to be for pages to load
        self.browser.implicitly_wait(3)

    def tearDown(self):
        """
        This method is run after all tests are finished
        """
        self.browser.quit()

    def test_can_start_a_list_and_retrive_it_later(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Home', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h4').text
        self.assertIn('Recent Blog Posts', header_text)
        
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), "Enter a to-do item")
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(10)
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(any(row.text == '1: Buy peakock feathers' for row in rows), "New to-do item did not appear in table")
        
        self.fail('Finish the test')
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')