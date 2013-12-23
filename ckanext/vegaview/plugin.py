import logging

import ckan.plugins as p

log = logging.getLogger(__name__)
not_empty = p.toolkit.get_validator('not_empty')
ignore_empty = p.toolkit.get_validator('ignore_empty')
natural_number_validator = p.toolkit.get_validator('natural_number_validator')


class VegaView(p.SingletonPlugin):
    '''This extension makes views of images'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'vegaview')

    def info(self):
        schema = {
            'vega_specification': [not_empty, unicode],
            'limit': [ignore_empty, natural_number_validator],
            'offset': [ignore_empty, natural_number_validator]
        }

        return {'name': 'vega',
                'title': 'Vega',
                'icon': 'bar-chart',
                'schema': schema,
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        vega_specification = data_dict['resource_view'].get('vega_specification', {})
        limit = data_dict['resource_view'].get('limit')
        offset = data_dict['resource_view'].get('offset')
        records = _get_records_from_datastore(data_dict['resource'], limit, offset)
        return {'vega_specification': vega_specification,
                'records': records}

    def view_template(self, context, data_dict):
        return 'vega_view.html'

    def form_template(self, context, data_dict):
        return 'vega_form.html'


def _get_records_from_datastore(resource, limit, offset):
    data = {'resource_id': resource['id'], 'limit': limit, 'offset': offset}
    records = p.toolkit.get_action('datastore_search')({}, data)['records']
    return records
