import socket
import time

from fh6_radio_clean_v02 import Runtime, UdpAddress, UdpService


def test_udp_service_receives_packet_and_stops():
    port = _free_port()
    runtime = Runtime()
    service = UdpService(runtime, UdpAddress("127.0.0.1", port))
    service.start()
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = bytearray(324)
        sender.sendto(data, ("127.0.0.1", port))
        deadline = time.time() + 1.0
        while time.time() < deadline and runtime.last_status.publication.current_scene.value == "STOPPED":
            time.sleep(0.01)
        assert runtime.last_status.publication.connection_status == "CONNECTED"
    finally:
        sender.close()
        service.stop()
    assert not service.running


def _free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port
