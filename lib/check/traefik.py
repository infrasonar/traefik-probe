from libprobe.asset import Asset
from libprobe.check import Check
from ..api_requests import api_requests
from ..utils import on_dt_str


class CheckTraefik(Check):
    key = 'traefik'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:
        resp = await api_requests(asset, config, (
            '/api/overview',
            '/api/version',
        ))
        data = resp['/api/overview']
        version = resp['/api/version']

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
