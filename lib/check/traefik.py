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
        protocol = config.get('protocol')
        if protocol == 'HTTPS (Unverified)':
            base_url = f'https://{address}:{port}'
        elif protocol == 'HTTPS (Strict)':
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

        overview = {
            f'{p}_{a}_{c}': d
            for p in ('http', 'tcp', 'udp')
            for a, b in data.get(p, {}).items()
            for c, d in b.items()
        }
        overview_cert = {
            f'certificates_{a}': b
            for a, b in data.get('certificates', {}).items()
        }
        return {
            'overview': [{
                'name': 'overview',
                **overview,
                **overview_cert,
            }],
            'version': [{
                'name': 'version',
                'version': version.get('Version'),
                'codename': version.get('Codename'),
                'start_ts': on_dt_str(version.get('startDate')),
            }],
        }
