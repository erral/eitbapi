from pyramid.config import Configurator
from pyramid.renderers import JSON
from .cors import cors_options_view
from .cors import NO_PERMISSION_REQUIRED
from .cors import add_cors_preflight_handler
from .cors import CorsPreflightPredicate
from .cors import add_cors_to_response


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    config.include("pyramid_chameleon")

    config.add_directive("add_cors_preflight_handler", add_cors_preflight_handler)
    config.add_route_predicate("cors_preflight", CorsPreflightPredicate)

    config.add_subscriber(add_cors_to_response, "pyramid.events.NewResponse")

    config.add_route(
        "cors-options-preflight", "/{catch_all:.*}", cors_preflight=True,
    )
    config.add_view(
        cors_options_view,
        route_name="cors-options-preflight",
        permission=NO_PERMISSION_REQUIRED,
    )

    config.add_renderer('prettyjson', JSON(indent=4, sort_keys=True))
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('programs', '/playlist')
    config.add_route('program-type-list', '/program-type-list')
    config.add_route('program-type-news', '/program-type-news')
    config.add_route('playlist', '/playlist/{playlist_id}')
    config.add_route('playlist-per-type', '/type-playlist/{playlist_id}')
    config.add_route('radio', '/radio')
    config.add_route('radio-program-type-list', '/radio-program-type-list')
    config.add_route('radio-playlist-per-type', '/type-rplaylist/{playlist_id}')
    config.add_route('radio-stations', '/radio-stations')
    config.add_route('radio-station-program-list', '/radio-station-programs/{station_id}')
    config.add_route('radioplaylist', '/rplaylist/{playlist_id:[a-zA-Z0-9\.\-\/]+}')
    config.add_route('episode', '/episode/{episode_url:[a-zA-Z0-9\.\-\/]+}')
    config.add_route('last-broadcast-list', '/last-broadcast-list')

    config.scan()
    return config.make_wsgi_app()
