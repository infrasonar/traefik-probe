import base64
from libprobe.asset import Asset
from libprobe.check import Check
from ..api_requests import api_requests


DEFAULT_PORT = 8080


class CheckData(Check):
    key = 'data'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:
        resp = await api_requests(asset, config, ('/api/rawdata', ))
        data = resp['/api/rawdata']

        routers = []
        for rname, r in data['routers'].items():
            item = {
                'name': rname,
                'entryPoints': r.get('entryPoints'),  # liststr
                'middlewares': r.get('middlewares'),  # liststr?
                'service': r.get('service'),  # str
                'rule': r.get('rule'),  # str
                'ruleSyntax': r.get('ruleSyntax'),  # str?
                'priority': r.get('priority'),  # int
                'status': r.get('status'),  # str
                'using': r.get('using'),  # liststr
            }
            for sname, s in data['services'].items():
                if rname in s.get('usedBy', []):
                    item['service'] = sname
                    break
            routers.append(item)

        middlewares = [{
            'name': mname,
            'status': m.get('status'),  # str
            'usedBy': m.get('usedBy'),  # liststr
        } for mname, m in data['middlewares'].items()]

        services = []
        for sname, s in data['services'].items():
            item = {
                'name': sname,
                'status': s.get('status'),  # str
                'usedBy': s.get('usedBy'),  # liststr
            }
            lb = s.get('loadBalancer')
            if lb:
                item['loadBalancerStrategy'] = lb.get('stategy')  # str?
                item['loadBalancerPassHostHeader'] = \
                    lb.get('passHostHeader')  # bool?
                item['loadBalancerServersTransport'] = \
                    lb.get('serversTransport')  # str?
                rf = lb.get('responseForwarding')
                if rf:
                    item['loadBalancerResponseForwardingFlushInterval'] = \
                        rf.get('flushInterval')  # str?
            services.append(item)

        server_status = [
            {
                'name': base64.b64encode(f'{sname}/{name}'.encode()).decode(),
                'server': name,
                'service': sname,
                'status': status,
            }
            for sname, s in data['services'].items()
            for name, status in s.get('serverStatus', {}).items()
        ]

        tcp_routers = []
        for rname, r in data['tcpRouters'].items():
            item = {
                'name': rname,
                'entryPoints': r.get('entryPoints'),  # liststr
                'service': r.get('service'),  # str
                'rule': r.get('rule'),  # str
                'priority': r.get('priority'),  # int
                'status': r.get('status'),  # str
                'using': r.get('using'),  # liststr
            }
            for sname, s in data['tcpServices'].items():
                if rname in s.get('usedBy', []):
                    item['service'] = sname
                    break
            tcp_routers.append(item)

        tcp_services = [{
            'name': mname,
            'status': m.get('status'),  # str
            'usedBy': m.get('usedBy'),  # liststr
        } for mname, m in data['tcpServices'].items()]

        tcp_server_status = [
            {
                'name': base64.b64encode(f'{sname}/{name}'.encode()).decode(),
                'server': name,
                'service': sname,
                'status': status,
            }
            for sname, s in data['tcpServices'].items()
            for name, status in s.get('serverStatus', {}).items()
        ]

        return {
            'routers': routers,
            'middlewares': middlewares,
            'services': services,
            'serverStatus': server_status,
            'tcpRouters': tcp_routers,
            'tcpServices': tcp_services,
            'tcpServerStatus': tcp_server_status,
        }
