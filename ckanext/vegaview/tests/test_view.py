import os
import inspect
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
