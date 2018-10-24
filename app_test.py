import unittest
from app import app

# functional tests for the app
class FunctionalTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    # ===================== Main View Test Cases =============== #

    def test_view_form_main(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Please enter your username and password", str(rv.data))

    # ===================== Map Test Cases ===================== #

    def test_map_psi(self):
        resp = self.client.get('/map/psi')
        self.assertEqual(resp.status, '200 OK')
        self.assertIn('maps.googleapis.com', str(resp.data))    # check if map is indeed loaded

    def test_map_weather(self):
        resp = self.client.get('/map/weather')
        self.assertEqual(resp.status, '200 OK')
        self.assertIn('maps.googleapis.com', str(resp.data))  # check if map is indeed loaded

    def test_map_shelters(self):
        resp = self.client.get('/map/shelters')
        self.assertEqual(resp.status, '200 OK')
        self.assertIn('maps.googleapis.com', str(resp.data))  # check if map is indeed loaded

    def test_map_dengue(self):
        resp = self.client.get('/map/dengue')
        self.assertEqual(resp.status, '200 OK')
        self.assertIn('maps.googleapis.com', str(resp.data))  # check if map is indeed loaded

    def test_map_incidents(self):
        resp = self.client.get('/map/incidents')
        self.assertEqual(resp.status, '200 OK')
        self.assertIn('maps.googleapis.com', str(resp.data))  # check if map is indeed loaded

    # ===================== Dashboard Test Cases ===================== #

    def test_dashboard_page(self):
        post_data = {'username': 'admin_test', 'password':'admin_test', 'role':'Admin'}
        rv = self.client.post('/', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Dashboard", str(rv.data))
        self.assertIn("Crisis Statistics", str(rv.data))

        # test if all tab values exists
        self.assertIn("Crisis Map", str(rv.data))
        self.assertIn("Incident Reporting", str(rv.data))
        self.assertIn("Account Management", str(rv.data))
        self.assertIn("Status Report", str(rv.data))

    # ===================== Account Management Test Cases ===================== #

    def test_login(self):
        post_data = {'username': 'admin_test', 'password': 'admin_test', 'role': 'Admin'}
        rv = self.client.post('/login', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Dashboard", str(rv.data))

        post_data = {'username': 'aaa', 'password': 'bbb', 'role': 'ccc'}
        rv = self.client.post('/login', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Invalid Credentials. Please try again", str(rv.data))

    def test_logout(self):
        resp = self.client.get('/logout')
        self.assertEqual(resp.status, '302 FOUND')

    def test_register(self):
        post_data = {'hf-username': 'govd0003', 'hf-password': 'Abcabc123A', 'select': 'Admin'}
        rv = self.client.post('/account/register', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')

    def test_deregister(self):
        post_data = {'hf-username': 'govd0003'}
        rv = self.client.post('/account/deregister', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')

    # ===================== Incident Report Test Cases ===================== #

    def test_submit_incident(self):
        post_data = {'caller_name': 'testing', 'caller_mobile_number': '12345678', 'caller_location': 'NTU',
                     'type_of_assistance' : '1', 'description': '123', 'priority_for_severity_of_injuries': '1',
                     'priority_for_impending_dangers': '1', 'priority_for_presence_of_nearby_help': '1',
                     'report_status': '1'}
        rv = self.client.post('/callcenter/submit_new_incident_report', data=post_data, follow_redirects=True)
        self.assertEqual(rv.status, '200 OK')
        self.assertIn("has been successfully submitted", str(rv.data))

    def test_update_incident(self):
        # I have problems loading the update page. need to consult call center team. #
        pass

    def test_delete_incident(self):
        # I have problems loading the delete page. need to consult call center team. #
        pass

    # ===================== Status Report Test Cases ===================== #

    def test_report(self):
        post_data = {'username': 'admin_test', 'password': 'admin_test', 'role': 'Admin'}
        self.client.post('/login', data=post_data, follow_redirects=True)
        rv = self.client.get('/report')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn("Status Report", str(rv.data))

    def test_download_report(self):
        post_data = {'username': 'admin_test', 'password': 'admin_test', 'role': 'Admin'}
        self.client.post('/login', data=post_data, follow_redirects=True)
        rv = self.client.get('/download/Status Report @ 2018-10-24 23:15:26.html')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn("Dear Prime Minister,", str(rv.data))

    def test_send_report(self):     # may fail, SMTPServer is unstable
        post_data = {'username': 'admin_test', 'password': 'admin_test', 'role': 'Admin'}
        self.client.post('/login', data=post_data, follow_redirects=True)
        rv = self.client.get('/send_now')
        self.assertEqual(rv.status, '302 FOUND')


if __name__ == '__main__':
    unittest.main()