#!/usr/bin/python3

try:
    import autotest.common as common  # pylint: disable=W0611
except ImportError:
    from . import common  # pylint: disable=W0611
import unittest

# This has to be done very early.
from autotest.client.shared.settings import settings
settings.override_value('HOSTS', 'default_protection', 'NO_PROTECTION')

from autotest.frontend import setup_django_environment  # pylint: disable=W0611
from autotest.frontend import setup_test_environment  # pylint: disable=W0611
from autotest.frontend.shared import resource_test_utils
from autotest.frontend.afe import control_file, models, model_attributes


class AfeResourceTestCase(resource_test_utils.ResourceTestCase):
    URI_PREFIX = 'http://testserver/afe/server/resources'

    CONTROL_FILE_CONTENTS = 'my control file contents'

    def setUp(self):
        super(AfeResourceTestCase, self).setUp()
        self._add_additional_data()

    def _add_additional_data(self):
        models.Test.objects.create(name='mytest',
                                   test_type=model_attributes.TestTypes.SERVER,
                                   path='/path/to/mytest')


class FilteringPagingTest(AfeResourceTestCase):
    # we'll arbitrarily choose to use hosts for this

    def setUp(self):
        super(FilteringPagingTest, self).setUp()

        self.labels[0].host_set = [self.hosts[0], self.hosts[1]]
        for host in self.hosts[:3]:
            host.locked = True
            host.save()

    def test_simple_filtering(self):
        response = self.request('get', 'hosts?locked=true&has_label=label1')
        self.check_collection(response, 'hostname', ['host1', 'host2'])

    def test_in_filtering(self):
        response = self.request('get', 'hosts?hostname:in=host1,host2')
        self.check_collection(response, 'hostname', ['host1', 'host2'])

    def test_paging(self):
        response = self.request('get', 'hosts?start_index=1&items_per_page=2')
        self.check_collection(response, 'hostname', ['host2', 'host3'])
        self.assertEqual(response['total_results'], 9)
        self.assertEqual(response['items_per_page'], 2)
        self.assertEqual(response['start_index'], 1)

    def test_full_representations(self):
        response = self.request(
            'get', 'hosts?hostname=host1&full_representations=true')
        self.check_collection(response, 'hostname', ['host1'])
        host = response['members'][0]
        # invalid only included in full representation
        self.assertEqual(host['invalid'], False)


class MiscellaneousTest(AfeResourceTestCase):

    def test_trailing_slash(self):
        response = self.request('get', 'hosts/host1/')
        self.assertEqual(response['hostname'], 'host1')


class AtomicGroupClassTest(AfeResourceTestCase):

    def test_collection(self):
        response = self.request('get', 'atomic_group_classes')
        self.check_collection(response, 'name', ['atomic1', 'atomic2'],
                              length=2)

    def test_entry(self):
        response = self.request('get', 'atomic_group_classes/atomic1')
        self.assertEqual(response['name'], 'atomic1')
        self.assertEqual(response['max_number_of_machines'], 2)

    def test_labels(self):
        self.check_relationship('atomic_group_classes/atomic1', 'labels',
                                'label', 'name', ['label4', 'label5'])


class LabelTest(AfeResourceTestCase):

    def test_collection(self):
        response = self.request('get', 'labels')
        self.check_collection(response, 'name', ['label1', 'label2'], length=9,
                              check_number=2)
        label1 = self.sorted_by(response['members'], 'name')[0]
        self.assertEqual(label1['is_platform'], False)

    def test_entry(self):
        response = self.request('get', 'labels/label1')
        self.assertEqual(response['name'], 'label1')
        self.assertEqual(response['is_platform'], False)
        self.assertEqual(response['atomic_group_class'], None)

    def test_hosts(self):
        self.check_relationship('labels/label1', 'hosts', 'host', 'hostname',
                                ['host1'])


class UserTest(AfeResourceTestCase):

    def test_collection(self):
        response = self.request('get', 'users')
        self.check_collection(response, 'username',
                              ['autotest_system', 'debug_user'])

    def test_entry(self):
        response = self.request('get', 'users/debug_user')
        self.assertEqual(response['username'], 'debug_user')

        me_response = self.request('get', 'users/@me')
        self.assertEqual(response, me_response)

    def test_acls(self):
        self.check_relationship('users/debug_user', 'acls', 'acl', 'name',
                                ['Everyone', 'my_acl'])

    def test_accessible_hosts(self):
        group = models.AclGroup.objects.create(name='mygroup')
        models.User.objects.get(login='debug_user').aclgroup_set = [group]
        self.hosts[0].aclgroup_set = [group]

        user = self.request('get', 'users/debug_user')
        response = self.request('get', user['accessible_hosts']['href'])
        self.check_collection(response, 'hostname', ['host1'])


class AclTest(AfeResourceTestCase):

    def test_collection(self):
        response = self.request('get', 'acls')
        self.check_collection(response, 'name', ['Everyone', 'my_acl'])

    def test_entry(self):
        response = self.request('get', 'acls/my_acl')
        self.assertEqual(response['name'], 'my_acl')

    def test_users(self):
        self.check_relationship('acls/my_acl', 'users', 'user', 'username',
                                ['autotest_system', 'debug_user'])

    def test_hosts(self):
        self.check_relationship('acls/my_acl', 'hosts', 'host', 'hostname',
                                ['host1', 'host2'], length=9, check_number=2)


class HostTest(AfeResourceTestCase):

    def test_collection(self):
        response = self.request('get', 'hosts')
        self.check_collection(response, 'hostname', ['host1', 'host2'],
                              length=9, check_number=2)
        host1 = self.sorted_by(response['members'], 'hostname')[0]
        self.assertEqual(host1['platform']['name'], 'myplatform')
        self.assertEqual(host1['locked'], False)
        self.assertEqual(host1['status'], 'Ready')

    def test_entry(self):
        response = self.request('get', 'hosts/host1')
        self.assertEqual(response['protection_level'], 'No protection')

    def test_labels(self):
        self.check_relationship('hosts/host1', 'labels', 'label', 'name',
                                ['label1', 'myplatform'])

    def test_acls(self):
        self.check_relationship('hosts/host1', 'acls', 'acl', 'name',
                                ['my_acl'])

    def test_queue_entries(self):
        self._create_job(hosts=[1])
        host = self.request('get', 'hosts/host1')
        entries = self.request('get', host['queue_entries']['href'])
        self.check_collection(entries, ['job', 'id'], [1])

    def test_health_tasks(self):
        models.SpecialTask.schedule_special_task(
            host=self.hosts[0], task=models.SpecialTask.Task.VERIFY)
        host = self.request('get', 'hosts/host1')
        tasks = self.request('get', host['health_tasks']['href'])
        self.check_collection(tasks, 'task_type', ['Verify'])

    def test_put(self):
        response = self.request('put', 'hosts/host1', data={'locked': True})
        self.assertEqual(response['locked'], True)
        response = self.request('get', 'hosts/host1')
        self.assertEqual(response['locked'], True)
        self.assertEqual(response['locked_by']['username'], 'debug_user')

    def test_post(self):
        data = {'hostname': 'newhost',
                'platform': {'href': self.URI_PREFIX + '/labels/myplatform'},
                'protection_level': 'Do not verify'}
        response = self.request('post', 'hosts', data=data)
        self.assertEqual(response, self.URI_PREFIX + '/hosts/newhost')

        host = models.Host.objects.get(hostname='newhost')
        self.assertEqual(host.platform().name, 'myplatform')
        self.assertEqual(host.protection, models.Host.Protection.DO_NOT_VERIFY)

    def _check_labels(self, host, expected_labels):
        label_names = sorted(label.name for label in host.labels.all())
        self.assertEqual(label_names, sorted(expected_labels))

    def test_add_label(self):
        labels_href = self.request('get', 'hosts/host1')['labels']['href']
        data = {'label': self.URI_PREFIX + '/labels/label2'}
        response = self.request('post', labels_href, data=data)
        self._check_labels(self.hosts[0], ['label1', 'label2', 'myplatform'])

    def test_remove_label(self):
        labels_href = self.request('get', 'hosts/host1')['labels']['href']
        labels_href += '&label=label1'
        labelings = self.request('get', labels_href)['members']
        self.assertEqual(len(labelings), 1)
        self.request('delete', labelings[0]['href'])
        self._check_labels(self.hosts[0], ['myplatform'])

    def test_delete(self):
        self.request('delete', 'hosts/host1')
        hosts = models.Host.valid_objects.filter(hostname='host1')
        self.assertEqual(len(hosts), 0)


class TestTest(AfeResourceTestCase):  # yes, we're testing the "tests" resource

    def test_collection(self):
        response = self.request('get', 'tests')
        self.check_collection(response, 'name', ['mytest'])

    def test_entry(self):
        response = self.request('get', 'tests/mytest')
        self.assertEqual(response['name'], 'mytest')
        self.assertEqual(response['control_file_type'], 'Server')
        self.assertEqual(response['control_file_path'], '/path/to/mytest')

    def test_dependencies(self):
        models.Test.objects.get(name='mytest').dependency_labels = [self.label3]
        self.check_relationship('tests/mytest', 'dependencies', 'label', 'name',
                                ['label3'])


class ExecutionInfoTest(AfeResourceTestCase):

    def setUp(self):
        super(ExecutionInfoTest, self).setUp()

        def mock_read_control_file(test):
            return self.CONTROL_FILE_CONTENTS
        self.god.stub_with(control_file, 'read_control_file',
                           mock_read_control_file)

    def test_get(self):
        response = self.request('get', 'execution_info?tests=mytest')
        info = response['execution_info']
        self.assertTrue(self.CONTROL_FILE_CONTENTS in info['control_file'])
        self.assertEqual(info['is_server'], True)
        self.assertEqual(info['machines_per_execution'], 1)


class QueueEntriesRequestTest(AfeResourceTestCase):

    def test_get(self):
        response = self.request(
            'get',
            'queue_entries_request?hosts=host1,host2&meta_hosts=label1')

        # choose an arbitrary but consistent ordering to ease checking
        def entry_href(entry):
            if 'host' in entry:
                return entry['host']['href']
            return entry['meta_host']['href']
        entries = sorted(response['queue_entries'], key=entry_href)

        expected = [
            {'host': {'href': self.URI_PREFIX + '/hosts/host1'}},
            {'host': {'href': self.URI_PREFIX + '/hosts/host2'}},
            {'meta_host': {'href': self.URI_PREFIX + '/labels/label1'}}]
        self.assertEqual(entries, expected)


class JobTest(AfeResourceTestCase):

    def setUp(self):
        super(JobTest, self).setUp()

        for _ in range(2):
            self._create_job(hosts=[1, 2])

        job = models.Job.objects.get(id=1)
        job.control_file = self.CONTROL_FILE_CONTENTS
        job.save()

        models.JobKeyval.objects.create(job=job, key='mykey', value='myvalue')

    def test_collection(self):
        response = self.request('get', 'jobs')
        self.check_collection(response, 'id', [1, 2])

    def test_keyval_filtering(self):
        response = self.request('get', 'jobs?has_keyval=mykey=myvalue')
        self.check_collection(response, 'id', [1])

    def test_entry(self):
        response = self.request('get', 'jobs/1')
        self.assertEqual(response['id'], 1)
        self.assertEqual(response['name'], 'test')
        self.assertEqual(response['keyvals'], {'mykey': 'myvalue'})
        info = response['execution_info']
        self.assertEqual(info['control_file'], self.CONTROL_FILE_CONTENTS)
        self.assertEqual(info['is_server'], False)
        self.assertEqual(info['cleanup_before_job'], 'Never')
        self.assertEqual(info['cleanup_after_job'], 'Always')
        self.assertEqual(info['machines_per_execution'], 1)
        self.assertEqual(info['run_verify'], True)

    def test_queue_entries(self):
        job = self.request('get', 'jobs/1')
        entries = self.request('get', job['queue_entries']['href'])
        self.check_collection(entries, ['host', 'hostname'], ['host1', 'host2'])

    def _test_post_helper(self, owner):
        data = {'name': 'myjob',
                'execution_info': {'control_file': self.CONTROL_FILE_CONTENTS,
                                   'is_server': True},
                'owner': owner,
                'drone_set': models.DroneSet.default_drone_set_name(),
                'queue_entries':
                [{'host': {'href': self.URI_PREFIX + '/hosts/host1'}},
                 {'host': {'href': self.URI_PREFIX + '/hosts/host2'}}]}
        response = self.request('post', 'jobs', data=data)
        self.assertEqual(response, self.URI_PREFIX + '/jobs/3')
        job = models.Job.objects.get(id=3)
        self.assertEqual(job.name, 'myjob')
        self.assertEqual(job.control_file, self.CONTROL_FILE_CONTENTS)
        self.assertEqual(job.control_type, models.Job.ControlType.SERVER)
        entries = job.hostqueueentry_set.order_by('host__hostname')
        self.assertEqual(entries[0].host.hostname, 'host1')
        self.assertEqual(entries[1].host.hostname, 'host2')

        owner_test = owner
        if not owner_test:
            owner_test = models.User.current_user().login
        self.assertEqual(job.owner, owner_test)

    def test_post_no_owner(self):
        self._test_post_helper(None)

    def test_post_with_owner(self):
        self._test_post_helper('job_owner')


class DirectoryTest(AfeResourceTestCase):

    def test_get(self):
        response = self.request('get', '')
        for key in ('atomic_group_classes', 'labels', 'users', 'acl_groups',
                    'hosts', 'tests', 'jobs', 'execution_info',
                    'queue_entries_request'):
            self.assertTrue(key in response)


if __name__ == '__main__':
    unittest.main()
