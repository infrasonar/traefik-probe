import aiohttp
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from .connector import get_connector


DEFAULT_PORT = 8080


async def api_requests(
        asset: Asset,
        config: dict,
        requests: tuple[str, ...]) -> dict:

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

    results = {}
    try:
        async with aiohttp.ClientSession(connector=get_connector()) as se:
            for r in requests:
                async with se.get(f'{base_url}{r}', ssl=ssl) as resp:
                    resp.raise_for_status()
                    results[r] = await resp.json()

    except Exception as e:
        msg = str(e) or type(e).__name__
        raise CheckException(msg)
