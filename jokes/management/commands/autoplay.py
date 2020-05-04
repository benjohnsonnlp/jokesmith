import time
import uuid

from django.core.management.base import BaseCommand
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from jokes.models import Session


class Command(BaseCommand):

    help = 'Use selenium to script a session among three imaginary players.'
    sleep_time = 5.0

    def get_browsers(self):
        self.stdout.write(self.style.SUCCESS("Starting up browsers..."))
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return (
            webdriver.Chrome(chrome_options=chrome_options),
            webdriver.Chrome(chrome_options=chrome_options),
            webdriver.Chrome(chrome_options=chrome_options),
        )

    def sleep(self):
        time.sleep(self.sleep_time)

    def handle(self, *args, **options):
        browsers = self.get_browsers()
        session_name = "testsession-{}".format(str(uuid.uuid4()))
        try:
            url = "http://localhost:8000" + reverse('index')
            self.stdout.write(self.style.SUCCESS("Joining a session..."))
            for i, browser in enumerate(browsers):
                browser.implicitly_wait(10)
                browser.get(url)

                elem = browser.find_element_by_id('username')  # Find the search box
                elem.send_keys('testuser' + str(i) + Keys.RETURN)

                elem = browser.find_element_by_id('session_name')
                elem.send_keys(session_name + Keys.RETURN)
            self.sleep()

            for browser in browsers:
                button = browser.find_element_by_id('readyButton')
                button.click()
            self.sleep()

            browser = browsers[0]
            button = browser.find_element_by_id('readyButton')
            self.stdout.write(self.style.SUCCESS("Submitting prompts..."))
            for browser in browsers:
                button = browser.find_element_by_id('submitPrompt')
                button.click()

            self.sleep()

            self.stdout.write(self.style.SUCCESS("Submitting responses..."))
            for i, browser in enumerate(browsers):
                button = browser.find_element_by_id('submitResponse')
                text = browser.find_element_by_id('responseText')
                text.send_keys('response from ' + str(i))
                button.click()

            self.sleep()

            for i, browser in enumerate(browsers):
                button = browser.find_element_by_id('submitResponse')
                text = browser.find_element_by_id('responseText')
                text.send_keys('2nd response from ' + str(i))
                button.click()

            self.stdout.write(self.style.SUCCESS("Okay, we're all done! Hit enter to quit."))
            input(">")

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Something went wrong:\n{exc}"))

        for browser in browsers:
            browser.quit()
        self.stdout.write(self.style.SUCCESS("Browsers closed."))

        try:
            session = Session.objects.get(name=session_name)
        except Session.DoesNotExist:
            pass
        else:
            session.delete()
            self.stdout.write(self.style.SUCCESS(f'Test session "{session_name}" removed.'))
