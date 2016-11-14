from pyramid.config import Configurator
from pyramid.renderers import JSON


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_renderer('prettyjson', JSON(indent=4, sort_keys=True))
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('programs', '/playlist')
    config.add_route('radio', '/radio')
    config.add_route('playlist', '/playlist/{playlist_id}')
    config.add_route('radioplaylist', '/rplaylist/{playlist_id:[a-zA-Z0-9\.\-\/]+}')
    config.add_route('episode', '/episode/{episode_url:[a-zA-Z0-9\.\-\/]+}')
    config.scan()
    return config.make_wsgi_app()
