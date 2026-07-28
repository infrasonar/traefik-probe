import aiohttp
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException
from ..connector import get_connector
from ..utils import on_dt_str


DEFAULT_PORT = 8080


class CheckTraefik(Check):
    key = 'traefik'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:
        address = config.get('address')
        if not address:
            address = asset.name
        port = config.get('port', DEFAULT_PORT)
        base_url = f'http://{address}:{port}'
        ssl = False
        schema = config.get('schema')
        if schema == 'HTTPS (Unverified)':
            base_url = f'https://{address}:{port}'
        elif schema == 'HTTPS (Strict)':
            base_url = f'https://{address}:{port}'
            ssl = True

        try:
            async with aiohttp.ClientSession(connector=get_connector()) as se:
                async with se.get(f'{base_url}/api/overview', ssl=ssl) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                async with se.get(f'{base_url}/api/version', ssl=ssl) as resp:
                    resp.raise_for_status()
                    version = await resp.json()
        except Exception as e:
            msg = str(e) or type(e).__name__
            raise CheckException(msg)

        state = {
            'traefik': [{
                'name': 'traefik',
                'version': version.get('Version'),
                'version_codename': version.get('Codename'),
                'version_start_date': on_dt_str(version.get('StartDate')),
            }],
        }

        http = data.get('http')
        if http:
            routers = http.get('routers')
            services = http.get('services')
            middlewares = http.get('middlewares')
            if routers:
                state['http_routers'] = [{
                    'name': 'routers'
                    **routers,
                }]
            if services:
                state['http_services'] = [{
                    'name': 'services'
                    **services,
                }]
            if middlewares:
                state['http_middlewares'] = [{
                    'name': 'middlewares'
                    **middlewares,
                }]

        tcp = data.get('tcp')
        if tcp:
            routers = tcp.get('routers')
            services = tcp.get('services')
            middlewares = tcp.get('middlewares')
            if routers:
                state['tcp_routers'] = [{
                    'name': 'routers'
                    **routers,
                }]
            if services:
                state['tcp_services'] = [{
                    'name': 'services'
                    **services,
                }]
            if middlewares:
                state['tcp_middlewares'] = [{
                    'name': 'middlewares'
                    **middlewares,
                }]

        udp = data.get('udp')
        if udp:
            routers = udp.get('routers')
            services = udp.get('services')
            middlewares = udp.get('middlewares')  # optional
            if routers:
                state['udp_routers'] = [{
                    'name': 'routers'
                    **routers,
                }]
            if services:
                state['udp_services'] = [{
                    'name': 'services'
                    **services,
                }]
            if middlewares:
                state['udp_middlewares'] = [{
                    'name': 'middlewares'
                    **middlewares,
                }]

        return state
