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

    def test_vega_specification_is_added_to_schema(self):
        schema = self.plugin.info().get('schema')
        assert schema is not None, 'Plugin should define schema'
        assert schema.get('vega_specification') is not None, 'Scheme should define "vega_specification"'

    def test_vega_specification_is_required(self):
        schema = self.plugin.info()['schema']
        not_empty = p.toolkit.get_validator('not_empty')
        assert not_empty in schema['vega_specification'], '"vega_specification" schema should be required'

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
            'resource': { 'id': 'an id'},
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
        resource_id = 'resource id'
        data_dict = {
            'resource': { 'id': resource_id},
            'resource_view': {}
        }
        template_variables = self.plugin.setup_template_variables(context,
                                                                  data_dict)
        get_action.assert_called_with('datastore_search')
        get_action().assert_called_with({}, {'resource_id': resource_id,
                                             'limit': 100000})
        assert template_variables.get('data') is not None
        assert template_variables['data'] == data, template_variables['data']
