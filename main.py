from libprobe.probe import Probe
from lib.check.traefik import CheckTraefik
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckTraefik,
    )

    probe = Probe("traefik", version, checks)

    probe.start()
