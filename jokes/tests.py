from contextlib import contextmanager
import time

from channels.testing import ChannelsLiveServerTestCase
from django.test import override_settings, TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from jokes.models import Prompt


class PromptTestCase(TestCase):

    fixtures = ['prompts.json']

    def test_sampling(self):
        sample_ids = set(p.pk for p in Prompt.random_set(5))
        self.assertEqual(len(sample_ids), 5)
        self.assertTrue(sample_ids <= set(range(1, 7)))

        sample_ids = [p.pk for p in Prompt.random_set(10)]
        self.assertEqual(len(sample_ids), 10)
        self.assertTrue(set(sample_ids) <= set(range(1, 7)))


class WorkflowTests(TestCase):

    SLEEP_TIME = 2.0

    fixtures = ['prompts.json']

    @contextmanager
    def browser(self, view_name: str):
        url = "{}{}".format('http://localhost:8000', reverse(view_name))
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(chrome_options=chrome_options)

        browser.get(url)
        yield browser
        browser.quit()

    def test_login(self):
        with self.browser("index") as page:
            elem = page.find_element_by_id('username')  # Find the search box
            elem.send_keys('testuser' + Keys.RETURN)
            elem = page.find_element_by_id('session_name')
            self.assertIsNotNone(elem)

    def test_join_session(self):
        with self.browser("index") as page:
            elem = page.find_element_by_id('username')  # Find the search box
            elem.send_keys('testuser' + Keys.RETURN)

            elem = page.find_element_by_id('session_name')
            elem.send_keys('testsession' + Keys.RETURN)

            elem = page.find_element_by_id('chat-message-input')
            elem.send_keys('test message' + Keys.RETURN)

            time.sleep(self.SLEEP_TIME)
            elem = page.find_element_by_css_selector('.card-body')
            self.assertIsNotNone(elem)

    def test_all(self):
        with self.browser('index') as browser_a, \
                self.browser('index') as browser_b, \
                self.browser('index') as browser_c:
            browsers = (browser_a, browser_b, browser_c)
            print("Logging test users in...")
            for i, browser in enumerate(browsers):
                elem = browser.find_element_by_id('username')  # Find the search box
                elem.send_keys('testuser' + str(i) + Keys.RETURN)

                elem = browser.find_element_by_id('session_name')
                elem.send_keys('testsession' + Keys.RETURN)

            time.sleep(self.SLEEP_TIME)
            print("Readying users...")
            for browser in browsers:
                button = browser.find_element_by_id('readyButton')
                button.click()

            time.sleep(self.SLEEP_TIME)


            browser = browsers[0]
            button = browser.find_element_by_id('readyButton')
            self.assertFalse(button.is_displayed())

            print("Bypassing prompt submission...")
            for browser in browsers:
                button = browser.find_element_by_id('submitPrompt')
                button.click()

            time.sleep(self.SLEEP_TIME)

            print("Submitting responses...")
            for i, browser in enumerate(browsers):
                button = browser.find_element_by_id('submitResponse')
                text = browser.find_element_by_id('responseText')
                text.send_keys('response from ' + str(i))
                button.click()

            time.sleep(self.SLEEP_TIME)

            print("Second round of response submission...")
            for i, browser in enumerate(browsers):
                button = browser.find_element_by_id('submitResponse')
                text = browser.find_element_by_id('responseText')
                text.send_keys('2nd response from ' + str(i))
                button.click()

            time.sleep(self.SLEEP_TIME)

            for i in range(3):
                print("Submitting votes (attempt #{})".format(i + 1))

                for i, browser in enumerate(browsers):
                    button = browser.find_element_by_class_name('voteRadio')
                    button.click()

                    button = browser.find_element_by_id('votingSubmit')
                    button.click()

                time.sleep(20)