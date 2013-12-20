import os
import inspect
import mock
import pylons.config as config

import ckan.plugins as p


class TestVegaView(object):

    @classmethod
    def setup_class(cls):
        p.load('vegaview')
        cls.plugin = p.get_plugin('vegaview')

    @classmethod
    def teardown_class(cls):
        p.unload('vegaview')

    def test_plugin_templates_path_is_added_to_config(self):
        filename = inspect.getfile(inspect.currentframe())
        path = os.path.dirname(filename)
        templates_path = os.path.abspath(path + "/../theme/templates")

        assert templates_path in config['extra_template_paths'], templates_path

    def test_plugin_isnt_iframed(self):
        # FIXME: It should be iframed, but I had a problem where the iframe
        # height keeps growing, and I wasn't sure how to fix it.
        iframed = self.plugin.info().get('iframed')
        assert not iframed, 'Plugin should not be iframed'

    def test_schema_exists(self):
        schema = self.plugin.info().get('schema')
        assert schema is not None, 'Plugin should define schema'

    def test_schema_has_vega_specification(self):
        schema = self.plugin.info()['schema']
        assert schema.get('vega_specification') is not None, 'Scheme should define "vega_specification"'

    def test_schema_vega_specification_is_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['vega_specification'],\
               '"vega_specification" should be required'

    def test_schema_vega_specification_converts_to_unicode(self):
        schema = self.plugin.info()['schema']
        assert unicode in schema['vega_specification'],\
               '"vega_specification" should be convert to unicode'

    def test_schema_has_limit(self):
        schema = self.plugin.info()['schema']
        assert schema.get('limit') is not None, 'Scheme should define "limit"'

    def test_schema_limit_isnt_required(self):
        schema = self.plugin.info()['schema']
        ignore_empty = p.toolkit.get_validator('ignore_empty')
        assert ignore_empty in schema['limit'], '"limit" shouldn\'t be required'

    def test_schema_limit_converts_to_int(self):
        schema = self.plugin.info()['schema']
        assert int in schema['limit'], '"limit" should converts to int'

    def test_schema_has_offset(self):
        schema = self.plugin.info()['schema']
        assert schema.get('offset') is not None, 'Scheme should define "offset"'

    def test_schema_offset_isnt_required(self):
        schema = self.plugin.info()['schema']
        ignore_empty = p.toolkit.get_validator('ignore_empty')
        assert ignore_empty in schema['offset'], '"offset" shouldn\'t be required'

    def test_schema_offset_converts_to_int(self):
        schema = self.plugin.info()['schema']
        assert int in schema['offset'], '"offset" should converts to int'

    def test_can_view_only_if_datastore_is_active(self):
        active_datastore_data_dict = {
            'resource': { 'datastore_active': True }
        }
        inactive_datastore_data_dict = {
            'resource': { 'datastore_active': False }
        }
        assert self.plugin.can_view(active_datastore_data_dict)
        assert not self.plugin.can_view(inactive_datastore_data_dict)

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_vega_specification(self, _):
        context = {}
        vega_specification = 'the vega specification'
        data_dict = {
            'resource': { 'id': 'resource id' },
            'resource_view': { 'vega_specification': vega_specification }
        }
        template_variables = self.plugin.setup_template_variables(context,
                                                                  data_dict)
        assert template_variables.get('vega_specification') is not None
        assert template_variables['vega_specification'] == vega_specification

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_adds_data_from_the_datastore(self, get_action):
        context = {}
        data = ['the', 'records']
        get_action.return_value.return_value = { 'records': data }
        data_dict = {
            'resource': { 'id': 'resource id' },
            'resource_view': {}
        }
        template_variables = self.plugin.setup_template_variables(context,
                                                                  data_dict)

        assert template_variables.get('data') is not None
        assert template_variables['data'] == data, template_variables['data']

    @mock.patch('ckan.plugins.toolkit.get_action')
    def test_setup_template_variables_calls_datastore_correctly(self, get_action):
        resource_id = 'resource id'
        limit = 51
        offset = 42
        context = {}
        data_dict = {
            'resource': { 'id': resource_id },
            'resource_view': { 'limit': limit, 'offset': offset }
        }
        template_variables = self.plugin.setup_template_variables(context,
                                                                  data_dict)
        get_action.assert_called_with('datastore_search')
        call_args_data = get_action().call_args[0][1]
        assert call_args_data['resource_id'] == resource_id,\
               call_args_data['resource_id']
        assert call_args_data['limit'] == limit, call_args_data['limit']
        assert call_args_data['offset'] == offset, call_args_data['offset']
