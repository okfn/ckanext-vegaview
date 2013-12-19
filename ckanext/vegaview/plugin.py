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
        return True

    def view_template(self, context, data_dict):
        return 'vega_view.html'

    def form_template(self, context, data_dict):
        return 'vega_form.html'
