"""
#  user_collections

"""
from django.test import RequestFactory
# from django.test import TestCase  # removed because it deletes test table data after every test
from unittest import TestCase
from django.test.client import Client
from django.contrib.auth.models import AnonymousUser, User
from importlib import import_module
from search.views import *
from results.views import *
from django.http import QueryDict

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_NAME = 'opus-test-cookie'

cursor = connection.cursor()

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_NAME = 'opus-test-cookie'
settings.CACHE_BACKEND = 'dummy:///'

class test_session(dict):
    """
    extends a dict object and adds a session_key attribute for use in this test suite

    because in django tests:

    session and authentication attributes must be supplied by the test itself if required for the view to function properly.
    ( via http://stackoverflow.com/questions/14714585/using-session-object-in-django-unit-test )

    in most cases a request.session = {} in the test itself would suffice
    but in user_collections views we also want to receive a string from request.session.session_key
    because that's how user collections tables are named

    extends the dict because that is how real sessions are interacted with

    """
    session_key = 'test_key'
    has_session = True


class user_CollectionsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def emptycollection(self):
        test_db = settings.DATABASES['default']['TEST']['NAME']
        cursor = connection.cursor()
        table_name = 'colls_' + test_session().session_key
        query = 'delete from %s.%s' % (test_db, table_name)
        print query
        cursor.execute(query)

    def test__edit_collection_add_one(self):
        self.emptycollection()
        action = 'add'
        request = self.factory.get('/opus/collections/default/add.json?request=1&ringobsid=S_IMG_CO_ISS_1680806160_N', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        request.session = test_session()
        response = edit_collection(request, ring_obs_id = 'S_IMG_CO_ISS_1680806160_N', action = action)
        print response.content
        self.assertEqual(response.status_code, 200)
        expected = '{"count": 1, "request_no": 1, "err": false}'
        self.assertEqual(expected, response.content)

    def test__edit_collection_remove_one(self):
        self.emptycollection()
        action = 'remove'
        request = self.factory.get('/opus/collections/default/add.json?request=1&ringobsid=S_IMG_CO_ISS_1680806160_N', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        request.session = test_session()
        response = edit_collection(request, ring_obs_id = 'S_IMG_CO_ISS_1680806160_N', action = action)
        print response.content
        self.assertEqual(response.status_code, 200)
        expected = '{"count": 0, "request_no": 1, "err": false}'
        self.assertEqual(expected, response.content)


    def test__edit_collection_add_range_reordered_columns(self):
        """ """
        self.emptycollection()
        action = 'addrange'
        ring_obs_id_min = 'S_IMG_CO_ISS_1688230251_N'
        ring_obs_id_max = 'S_IMG_CO_ISS_1688230566_N'

        url = '/opus/collections/default/addrange.json?request=1&addrange=%s,%s&volumeid=COISS_2069&view=browse&browse=gallery&colls_browse=gallery&order=timesec1&cols=primaryfilespec,time1,time2,ringobsid,observationduration,ringradius1,ringradius2,J2000longitude1,J2000longitude2,phase1,phase2,incidence1,incidence2,emission1,emission2'
        request = self.factory.get(url % (ring_obs_id_min, ring_obs_id_max), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        request.session = test_session()
        response = edit_collection(request, addrange = '%s,%s' % (ring_obs_id_min,ring_obs_id_max), action = action)

        print response.content
        self.assertEqual(response.status_code, 200)
        expected = '{"count": 4, "request_no": 1, "err": false}'
        self.assertEqual(expected, response.content)

    def test__edit_collection_add_range(self):
        """ """
        self.emptycollection()
        action = 'addrange'
        ring_obs_id_min = 'S_IMG_CO_ISS_1688230251_N'
        ring_obs_id_max = 'S_IMG_CO_ISS_1688230566_N'

        url = '/opus/collections/default/addrange.json?request=1&addrange=%s,%s&volumeid=COISS_2069&view=browse&browse=gallery&colls_browse=gallery&&order=timesec1'
        request = self.factory.get(url % (ring_obs_id_min, ring_obs_id_max), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        request.session = test_session()
        response = edit_collection(request, addrange = '%s,%s' % (ring_obs_id_min,ring_obs_id_max), action = action)

        print response.content
        self.assertEqual(response.status_code, 200)
        expected = '{"count": 4, "request_no": 1, "err": false}'
        self.assertEqual(expected, response.content)

    def test__edit_collection_remove_range(self):
        # lol just kidding
        pass

    def test__get_collection_table(self):
        self.emptycollection()
        session_id = test_session().session_key
        table_name = get_collection_table(session_id)
        self.assertEqual('colls_test_key', table_name)

    def test__bulk_add_to_collection(self):
        self.emptycollection()
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1692988072_N','S_IMG_CO_ISS_1692988234_N','S_IMG_CO_ISS_1692988460_N','S_IMG_CO_ISS_1692988500_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)
        expected = len(ring_obs_id_list)
        received = get_collection_count(session_id)
        self.assertEqual(expected, received)

    def test__get_collection_in_page(self):
        # this is awfully round about and should perhaps be part of results.views test suite

        # first add some to collection
        self.emptycollection()
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1688233102_N','S_IMG_CO_ISS_1688235606_N','S_IMG_CO_ISS_1688244278_N','S_IMG_CO_ISS_1688393550_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)

        # then do a request to get a page of results
        url = '/opus/api/data.json?volumeid=COISS_2069&view=browse&browse=gallery&colls_browse=gallery&page=1&gallery_data_viewer=true&limit=100&order=timesec1&cols=ringobsid,planet,target,phase1,time1,time2&widgets=planet,target&widgets2=&detail='
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.session = test_session()
        [page_no, limit, page, page_ids, order] = getPage(request)

        # then hand that page to the method we are trying to test
        cip = get_collection_in_page(page, session_id)
        self.assertEqual(cip, ring_obs_id_list)  # we get back what we put in

    def test__bulk_get_collection_csv_data(self):
        self.emptycollection()
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1688233102_N','S_IMG_CO_ISS_1688235606_N','S_IMG_CO_ISS_1688244278_N','S_IMG_CO_ISS_1688393550_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)

        url = '/opus/collections/data.csv?volumeid=COISS_2069&view=browse&browse=gallery&colls_browse=gallery&page=1&gallery_data_viewer=true&limit=100&order=timesec1&cols=ringobsid,planet,target,phase1,phase2,time1,time2,ringradius1,ringradius2,J2000longitude1,J2000longitude2'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.session = test_session()
        slugs, data = get_collection_csv(request, fmt="raw")
        print(slugs, data)
        self.assertGreater(len(slugs), 5)
        self.assertGreater(len(data), 3)


    def test__collection_get_csv(self):
        self.emptycollection()
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1688233102_N','S_IMG_CO_ISS_1688235606_N','S_IMG_CO_ISS_1688244278_N','S_IMG_CO_ISS_1688393550_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)

        url = '/opus/collections/data.csv?volumeid=COISS_2069&view=browse&browse=gallery&colls_browse=gallery&page=1&gallery_data_viewer=true&limit=100&order=timesec1&cols=ringobsid,planet,target,phase1,phase2,time1,time2,ringradius1,ringradius2,J2000longitude1,J2000longitude2'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.session = test_session()
        response = get_collection_csv(request)  # raw format
        print response.content
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 466)

    def test__get_collection_count(self):
        self.emptycollection()
        session_id = test_session().session_key
        count = get_collection_count(session_id)
        self.assertEqual(count, 0)  # nothing here yet

        # let's add some stuff
        ring_obs_id_list = ['S_IMG_CO_ISS_1688233102_N','S_IMG_CO_ISS_1688235606_N','S_IMG_CO_ISS_1688244278_N','S_IMG_CO_ISS_1688393550_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)
        count = get_collection_count(session_id)
        self.assertEqual(count, 4)  # nothing here yet

    def test__view_collection(self):
        self.emptycollection()
        # first add some to collection
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1692988072_N','S_IMG_CO_ISS_1692988234_N','S_IMG_CO_ISS_1692988460_N','S_IMG_CO_ISS_1692988500_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)

        # then request to view it
        url = '/opus/collections/default/view.html'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.session = test_session()
        response = view_collection(request, 'default', template="collections.html")
        print response.content
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.content), 5000)

    def test__check_collection_args(self):
        self.emptycollection()
        # first add some to collection
        session_id = test_session().session_key
        ring_obs_id_list = ['S_IMG_CO_ISS_1692988072_N','S_IMG_CO_ISS_1692988234_N','S_IMG_CO_ISS_1692988460_N','S_IMG_CO_ISS_1692988500_N']
        bulk_add_to_collection(ring_obs_id_list, session_id)

        # then request to view it
        url = '/opus/collections/default/view.html'
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.session = test_session()
        kwargs = {
            'request_no':1,
            'action':'addrange',
            'ring_obs_id':'catface',
            }
        received = check_collection_args(request,**kwargs)
        expected = ['addrange', 'catface', 1, 1]
        self.assertEqual(expected, received)

        kwargs = {
            'request_no':2,
            'action':'addrange',
            }
        received = check_collection_args(request,**kwargs)
        expected = 'No Observations specified'
        self.assertEqual(expected, received)
        self.emptycollection()
