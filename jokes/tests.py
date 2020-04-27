import time

from django.test import TestCase
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class WorkflowTests(TestCase):

    def test_login(self):
        browser = webdriver.Chrome()
        url = "http://localhost:8000" + reverse('index')
        browser.get(url)

        elem = browser.find_element_by_id('username')  # Find the search box
        elem.send_keys('testuser' + Keys.RETURN)

        elem = browser.find_element_by_id('session_name')
        self.assertIsNotNone(elem)

        browser.quit()

    def test_join_session(self):
        browser = webdriver.Chrome()
        url = "http://localhost:8000" + reverse('index')
        browser.get(url)

        elem = browser.find_element_by_id('username')  # Find the search box
        elem.send_keys('testuser' + Keys.RETURN)

        elem = browser.find_element_by_id('session_name')
        elem.send_keys('testsession' + Keys.RETURN)

        elem = browser.find_element_by_id('chat-message-input')
        elem.send_keys('test message' + Keys.RETURN)

        time.sleep(1)
        elem = browser.find_element_by_css_selector('.card-body')
        self.assertIsNotNone(elem)
        browser.quit()

    def test_all(self):
        browsers = [
            webdriver.Chrome(),
            webdriver.Chrome(),
            webdriver.Chrome(),
        ]

        url = "http://localhost:8000" + reverse('index')
        for i, browser in enumerate(browsers):
            browser.get(url)

            elem = browser.find_element_by_id('username')  # Find the search box
            elem.send_keys('testuser' + str(i) + Keys.RETURN)

            elem = browser.find_element_by_id('session_name')
            elem.send_keys('testsession' + Keys.RETURN)

        time.sleep(0.5)

        for browser in browsers:
            button = browser.find_element_by_id('readyButton')
            button.click()

        time.sleep(0.5)
        browser = browsers[0]
        button = browser.find_element_by_id('readyButton')
        self.assertFalse(button.is_displayed())

        for browser in browsers:
            button = browser.find_element_by_id('submitPrompt')
            button.click()

        time.sleep(0.5)

        for i, browser in enumerate(browsers):
            button = browser.find_element_by_id('submitResponse')
            text = browser.find_element_by_id('responseText')
            text.send_keys('response from ' + str(i))
            button.click()

        # input()  # for manual testing
        for browser in browsers:
            browser.quit()




