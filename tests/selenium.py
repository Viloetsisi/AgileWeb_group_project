import os
import threading
import time
import unittest
import tempfile
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Force test DB and suppress mail BEFORE importing app/db
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import application, db

def wait_for_port(port, host='127.0.0.1', timeout=10.0):
    print(f"[*] Waiting for {host}:{port} to be available...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), 1):
                print(f"[*] Port {port} is open!")
                return True
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"Server on {host}:{port} not responding after {timeout}s")

def run_app():
    print("[*] Flask thread: setting up app context and DB")
    # Force all test-safe config here
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False
    application.config['MAIL_SUPPRESS_SEND'] = True
    application.config['MAIL_SERVER'] = 'localhost'
    application.config['MAIL_PORT'] = 25
    application.config['MAIL_USERNAME'] = ''
    application.config['MAIL_PASSWORD'] = ''
    application.config['MAIL_DEFAULT_SENDER'] = ''
    application.config['MAIL_USE_TLS'] = False
    application.config['MAIL_USE_SSL'] = False
    with application.app_context():
        db.create_all()
    print("[*] Flask thread: running Flask app on port 5001")
    application.run(port=5001, use_reloader=False)
    print("[*] Flask thread: app.run() exited (should not happen unless shutting down)")

class SeleniumFlaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("[*] Starting Flask server thread...")
        cls.flask_thread = threading.Thread(target=run_app)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()
        wait_for_port(5001)

        print("[*] Starting headless Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        cls.browser = webdriver.Chrome(options=options)
        cls.base_url = 'http://127.0.0.1:5001'

        # -- Quick server healthcheck --
        print("[*] Checking /testping route before signup...")
        try:
            cls.browser.get(f'{cls.base_url}/testping')
            print("[*] /testping returned:", cls.browser.page_source)
        except Exception as e:
            print("[!] Could not GET /testping:", e)
            raise

        print("[*] Loading signup page in browser...")
        cls.browser.get(f'{cls.base_url}/signup')
        print("[*] Waiting for username input to be visible...")
        WebDriverWait(cls.browser, 10).until(EC.visibility_of_element_located((By.NAME, 'username')))
        print("[*] Filling signup form...")
        cls.browser.find_element(By.NAME, 'username').send_keys('testuser')
        cls.browser.find_element(By.NAME, 'email').send_keys('test@example.com')
        cls.browser.find_element(By.NAME, 'password').send_keys('123456')
        cls.browser.find_element(By.NAME, 'confirm_password').send_keys('123456')
        print("[*] Waiting for submit button to be clickable...")
        submit_btn = WebDriverWait(cls.browser, 10).until(
            EC.element_to_be_clickable((By.NAME, 'submit'))
        )
        cls.browser.execute_script("arguments[0].scrollIntoView();", submit_btn)
        try:
            submit_btn.click()
            print("[*] Submit button clicked (normal click).")
        except Exception as e:
            print(f"[!] Normal click failed: {e}")
            print("[*] Trying JavaScript click...")
            cls.browser.execute_script("arguments[0].click();", submit_btn)
            print("[*] JavaScript click attempted.")
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        print("[*] Quitting browser and cleaning up DB...")
        cls.browser.quit()
        with application.app_context():
            db.session.remove()
            db.drop_all()
        print("[*] Test run complete.")

    def login(self):
        print("[*] Logging in...")
        self.browser.get(f'{self.base_url}/login')
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.NAME, 'username')))
        self.browser.find_element(By.NAME, 'username').clear()
        self.browser.find_element(By.NAME, 'username').send_keys('testuser')
        self.browser.find_element(By.NAME, 'password').clear()
        self.browser.find_element(By.NAME, 'password').send_keys('123456')
        login_btn = self.browser.find_element(By.NAME, 'submit')
        self.browser.execute_script("arguments[0].scrollIntoView();", login_btn)
        login_btn.click()
        time.sleep(0.5)
        print(f"[*] Logged in! URL is now: {self.browser.current_url}")

    def test_1_login(self):
        self.login()
        self.assertIn('dashboard', self.browser.current_url)
        print("[*] Login test passed!")

    def test_2_edit_profile(self):
        self.login()
        self.browser.get(f'{self.base_url}/edit_profile')
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.NAME, 'full_name')))
        self.browser.find_element(By.NAME, 'full_name').clear()
        self.browser.find_element(By.NAME, 'full_name').send_keys('Test User')
        Select(self.browser.find_element(By.NAME, 'education')).select_by_visible_text('Bachelor')
        Select(self.browser.find_element(By.NAME, 'gpa')).select_by_visible_text('HD')
        Select(self.browser.find_element(By.NAME, 'communication_skill')).select_by_visible_text('5')
        # Use the exact text for working_experience
        select_elem = Select(self.browser.find_element(By.NAME, 'working_experience'))
        print("[*] working_experience options:", [o.text for o in select_elem.options])
        select_elem.select_by_visible_text('5+ years')
        profile_submit = self.browser.find_element(By.NAME, 'submit')
        self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", profile_submit)
        time.sleep(0.5)
        try:
            profile_submit.click()
            print("[*] Profile submit button clicked (normal click).")
        except Exception as e:
            print(f"[!] profile_submit normal click failed: {e}")
            self.browser.save_screenshot("profile_submit_error.png")
            self.browser.execute_script("arguments[0].click();", profile_submit)
            print("[*] JavaScript click attempted for profile submit.")
        time.sleep(0.5)
        self.assertTrue('/profile' in self.browser.current_url or '/edit_profile' in self.browser.current_url)
        print("[*] Profile edit test passed!")

    def test_3_upload_document(self):
        self.login()
        self.browser.get(f'{self.base_url}/upload_document')
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.NAME, 'data_file')))
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Test document for upload')
            tmp_path = tmp.name
        self.browser.find_element(By.NAME, 'data_file').send_keys(tmp_path)
        upload_submit = self.browser.find_element(By.NAME, 'submit')
        self.browser.execute_script("arguments[0].scrollIntoView();", upload_submit)
        upload_submit.click()
        time.sleep(1)
        self.assertIn('profile', self.browser.current_url)
        print("[*] Document upload test passed!")

    def test_4_job_history(self):
        self.login()
        self.browser.get(f'{self.base_url}/jobs')
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.NAME, 'company_name')))
        self.browser.find_element(By.NAME, 'company_name').send_keys('OpenAI')
        self.browser.find_element(By.NAME, 'position').send_keys('Researcher')
        self.browser.find_element(By.NAME, 'start_date').send_keys('2022-01-01')
        self.browser.find_element(By.NAME, 'end_date').send_keys('2022-12-31')
        job_submit = self.browser.find_element(By.NAME, 'submit')
        self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_submit)
        time.sleep(0.5)
        try:
            job_submit.click()
            print("[*] Job submit button clicked (normal click).")
        except Exception as e:
            print(f"[!] job_submit normal click failed: {e}")
            self.browser.save_screenshot("job_submit_error.png")
            self.browser.execute_script("arguments[0].click();", job_submit)
            print("[*] JavaScript click attempted for job submit.")
        time.sleep(0.5)
        self.assertIn('jobs', self.browser.current_url)
        print("[*] Job history test passed!")

    def test_5_access_market(self):
        self.login()
        self.browser.get(f'{self.base_url}/career_market')
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
        self.assertIn('career_market', self.browser.current_url)
        print("[*] Career market access test passed!")

if __name__ == '__main__':
    unittest.main()
