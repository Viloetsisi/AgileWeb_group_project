import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from threading import Thread
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import application


class LiveServerThread(Thread):
    def run(self):
        application.run(port=5001, debug=False, use_reloader=False)


class SeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = LiveServerThread()
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

        options = Options()
        options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)
        cls.base_url = "http://localhost:5001"

        cls.username = "selenium_user"
        cls.email = "selenium@example.com"
        cls.password = "password123"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def login(self):
        self.driver.get(self.base_url + "/login")
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(self.driver, 5).until_not(EC.url_contains("/login"))

    def test_1_signup_then_login(self):
        self.driver.get(self.base_url + "/signup")
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "confirm_password").send_keys(self.password)

        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.2)
        submit_btn.click()

        time.sleep(1)
        if "already exists" in self.driver.page_source or "Log In" in self.driver.page_source:
            self.login()

        self.assertIn("Dashboard", self.driver.page_source)

    def test_2_dashboard_access(self):
        self.login()
        self.driver.get(self.base_url + "/dashboard")
        self.assertIn("Job-Fit Score", self.driver.page_source)

    def test_3_edit_profile(self):
        self.login()
        self.driver.get(self.base_url + "/edit_profile")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "full_name"))
        )

        self.driver.find_element(By.NAME, "full_name").clear()
        self.driver.find_element(By.NAME, "full_name").send_keys("Selenium Test User")
        self.driver.find_element(By.NAME, "age").clear()
        self.driver.find_element(By.NAME, "age").send_keys("22")
        self.driver.find_element(By.NAME, "birth_date").send_keys("22-01-2001")

        Select(self.driver.find_element(By.NAME, "education")).select_by_visible_text("Bachelor")
        Select(self.driver.find_element(By.NAME, "gpa")).select_by_visible_text("HD")
        Select(self.driver.find_element(By.NAME, "communication_skill")).select_by_visible_text("4")
        Select(self.driver.find_element(By.NAME, "working_experience")).select_by_visible_text("2 years")

        self.driver.find_element(By.NAME, "school").send_keys("Test University")
        self.driver.find_element(By.NAME, "graduation_date").send_keys("23-12-2001")
        self.driver.find_element(By.NAME, "career_goal").send_keys("Software Engineer")
        self.driver.find_element(By.NAME, "self_description").send_keys("I am a test user.")
        self.driver.find_element(By.NAME, "internship_experience").send_keys("Intern at Test Inc.")

        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Updated condition to something guaranteed on the post-save page
        self.assertIn("Profile updated successfully", self.driver.page_source)
        self.assertIn("My Profile", self.driver.page_source)
        self.assertIn("Edit Profile", self.driver.page_source)


    def test_4_upload_document(self):
        self.login()
        self.driver.get(self.base_url + "/upload_document")

        test_file_path = os.path.abspath("test_resume.pdf")
        with open(test_file_path, "w") as f:
            f.write("Selenium test upload.")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "data_file"))
        )
        self.driver.find_element(By.NAME, "data_file").send_keys(test_file_path)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.assertIn("Document uploaded successfully", self.driver.page_source)
        os.remove(test_file_path)

    def test_5_add_job_history(self):
        self.login()
        self.driver.get(self.base_url + "/jobs")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "company_name"))
        )

        self.driver.find_element(By.NAME, "company_name").send_keys("TestCorp Pty Ltd")
        self.driver.find_element(By.NAME, "position").send_keys("Test Engineer")
        self.driver.find_element(By.NAME, "start_date").send_keys("01-01-2001")
        self.driver.find_element(By.NAME, "end_date").send_keys("20-01-2020")
        self.driver.find_element(By.NAME, "salary").send_keys("75000")
        self.driver.find_element(By.NAME, "description").send_keys("Worked on testing systems.")

        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        self.driver.execute_script("arguments[0].click();", submit_btn)

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        self.assertIn("TestCorp Pty Ltd", self.driver.page_source)
        self.assertIn("Test Engineer", self.driver.page_source)


if __name__ == "__main__":
    unittest.main()
