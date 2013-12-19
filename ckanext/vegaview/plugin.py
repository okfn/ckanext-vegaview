import logging

import ckan.plugins as p

log = logging.getLogger(__name__)
not_empty = p.toolkit.get_validator('not_empty')


class VegaView(p.SingletonPlugin):
    '''This extension makes views of images'''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'vegaview')

    def info(self):
        return {'name': 'vega',
                'title': 'Vega',
                'icon': 'bar-chart',
                'schema': {'vega_specification': [not_empty, unicode]},
                'iframed': False}

    def can_view(self, data_dict):
        return data_dict['resource'].get('datastore_active', False)

    def setup_template_variables(self, context, data_dict):
        vega_specification = data_dict['resource_view'].get('vega_specification', {})
        data = _get_records_from_datastore(data_dict['resource'])
        return {'vega_specification': vega_specification,
                'data': data}

    def view_template(self, context, data_dict):
        return 'vega_view.html'

    def form_template(self, context, data_dict):
        return 'vega_form.html'


def _get_records_from_datastore(resource):
    data = {'resource_id': resource['id'], 'limit': 100000}
    records = p.toolkit.get_action('datastore_search')({}, data)['records']
    return records
