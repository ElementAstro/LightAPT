import os
import ssl
from tornado.options import define

from .webutils import is_valid_encoding, parse_origin_from_url, to_ip_address
from .webssh.policy import load_host_keys , get_policy_class , check_policy_setting

from .logging import webssh_logger as logger

define('address', default='localhost', help='Listen address')
define('port', type=int, default=8080,  help='Listen port')
# SSL Mode support
define('ssladdress', default='localhost', help='SSL listen address')
define('sslport', type=int, default=4433,  help='SSL listen port')
define('certfile', default='', help='SSL certificate file')
define('keyfile', default='', help='SSL private key file')

define('policy', default='warning',
       help='Missing host key policy, reject|autoadd|warning')
define('hostfile', default='', help='User defined host keys file')
define('syshostfile', default='', help='System wide host keys file')

# Safety options
define('tdstream', default='', help='Trusted downstream, separated by comma')
define('redirect', type=bool, default=True, help='Redirecting http to https')
define('fbidhttp', type=bool, default=True,
       help='Forbid public plain http incoming requests')
define('xheaders', type=bool, default=True, help='Support xheaders')
define('xsrf', type=bool, default=True, help='CSRF protection')
define('origin', default='same', help='''Origin policy,
'same': same origin policy, matches host name and port number;
'primary': primary domain policy, matches primary domain only;
'<domains>': custom domains policy, matches any domain in the <domains> list
separated by comma;
'*': wildcard policy, matches any domain, allowed in debug mode only.''')
       
define('wpintvl', type=float, default=0, help='Websocket ping interval')
define('timeout', type=float, default=3, help='SSH connection timeout')
define('delay', type=float, default=3, help='The delay to call recycle_worker')
define('maxconn', type=int, default=20,
       help='Maximum live connections (ssh sessions) per client')
define('font', default='', help='custom font filename')
define('encoding', default='',
       help='''The default character encoding of ssh servers.
Example: --encoding='utf-8' to solve the problem with some switches&routers''')

# Debug Mode support
define('debug', type=bool, default=False, help='Debug mode')
define('autoreload', type=bool, default=False, help='Autoreload the resources')

max_body_size = 1 * 1024 * 1024

def get_app_settings(options):
    """
        Get the settings of the tornado application
        Args:
            options : tornado.options.options
        Returns: {
            template_path : str # path to the template files
            static_path : str # path to the static files
            websocket_ping_interval : int
            debug : bool # whether to enable debug mode
            autoreload : bool # whether to enable autoreload the server
            xsrf_cookies : cookie list
            origin_policy : list
        }
    """
    settings = dict(
        template_path=os.path.join(os.getcwd(), 'client' ,'templates'),
        static_path=os.path.join(os.getcwd(), 'client' , 'static'),
        websocket_ping_interval=options.wpintvl,
        debug=options.debug,
        autoreload = options.autoreload,
        xsrf_cookies=options.xsrf,
        origin_policy=get_origin_setting(options)
    )
    return settings


def get_server_settings(options) -> dict:

    settings = dict(
        xheaders=options.xheaders,
        max_body_size=max_body_size,
        trusted_downstream=get_trusted_downstream(options.tdstream)
    )
    return settings

def get_host_keys_settings(options):
    if not options.hostfile:
        host_keys_filename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'known_hosts')
    else:
        host_keys_filename = options.hostfile
    host_keys = load_host_keys(host_keys_filename)

    if not options.syshostfile:
        filename = os.path.expanduser('~/.ssh/known_hosts')
    else:
        filename = options.syshostfile
    system_host_keys = load_host_keys(filename)

    settings = dict(
        host_keys=host_keys,
        system_host_keys=system_host_keys,
        host_keys_filename=host_keys_filename
    )
    return settings


def get_policy_setting(options, host_keys_settings):
    policy_class = get_policy_class(options.policy)
    logger.info(policy_class.__name__)
    check_policy_setting(policy_class, host_keys_settings)
    return policy_class()


def get_ssl_context(options):
    if not options.certfile and not options.keyfile:
        return None
    elif not options.certfile:
        raise ValueError('certfile is not provided')
    elif not options.keyfile:
        raise ValueError('keyfile is not provided')
    elif not os.path.isfile(options.certfile):
        raise ValueError('File {!r} does not exist'.format(options.certfile))
    elif not os.path.isfile(options.keyfile):
        raise ValueError('File {!r} does not exist'.format(options.keyfile))
    else:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(options.certfile, options.keyfile)
        return ssl_ctx


def get_trusted_downstream(tdstream):
    result = set()
    for ip in tdstream.split(','):
        ip = ip.strip()
        if ip:
            to_ip_address(ip)
            result.add(ip)
    return result


def get_origin_setting(options):
    if options.origin == '*':
        if not options.debug:
            raise ValueError(
                'Wildcard origin policy is only allowed in debug mode.'
            )
        else:
            return '*'

    origin = options.origin.lower()
    if origin in ['same', 'primary']:
        return origin

    origins = set()
    for url in origin.split(','):
        orig = parse_origin_from_url(url)
        if orig:
            origins.add(orig)

    if not origins:
        raise ValueError('Empty origin list')

    return origins

def check_encoding_setting(encoding) -> None:
    """
        Check if the given encoding is supported . If not , just raise an exception
    """
    if encoding and not is_valid_encoding(encoding):
        raise ValueError('Unknown character encoding {!r}.'.format(encoding))