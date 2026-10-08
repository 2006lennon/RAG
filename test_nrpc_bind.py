from impacket.dcerpc.v5 import transport, nrpc, epm
import ipaddress


# ============================================================
# Configuration
# ============================================================

LAB_DC_IP = "192.168.10.10"

# 只允許 RFC1918 私有網路
ALLOW_PRIVATE_ONLY = True


# ============================================================
# Target validation
# ============================================================

def validate_target(ip_text):
    try:
        ip = ipaddress.ip_address(ip_text)
    except ValueError:
        print("[!] Invalid IP address.")
        return False

    if ALLOW_PRIVATE_ONLY and not ip.is_private:
        print("[!] BLOCKED: target must be a private lab IP.")
        return False

    return True


# ============================================================
# Main
# ============================================================

def main():
    if LAB_DC_IP == "192.168.10.10":
        print("[!] Please set LAB_DC_IP first.")
        return

    if not validate_target(LAB_DC_IP):
        return

    print("[*] Safe NRPC runtime validation")
    print(f"[*] Target: {LAB_DC_IP}")
    print("[*] Action: Endpoint Mapper lookup + NRPC bind")
    print("[*] No authentication attempt")
    print("[*] No password modification")
    print("[*] No credential dump")
    print("[*] No remote command")

    try:
        print("\n[*] Querying RPC Endpoint Mapper...")

        string_binding = epm.hept_map(
            LAB_DC_IP,
            nrpc.MSRPC_UUID_NRPC,
            protocol="ncacn_ip_tcp",
        )

        print(f"[+] NRPC endpoint found: {string_binding}")

        print("[*] Creating RPC transport...")

        rpc_transport = transport.DCERPCTransportFactory(
            string_binding
        )

        rpc_transport.setRemoteHost(LAB_DC_IP)

        dce = rpc_transport.get_dce_rpc()

        print("[*] Connecting...")

        dce.connect()

        print("[+] RPC connection established.")

        print("[*] Binding to MS-NRPC interface...")

        dce.bind(nrpc.MSRPC_UUID_NRPC)

        print("[+] NRPC bind successful.")
        print("[+] SAFE RUNTIME TEST PASSED")

        dce.disconnect()

    except Exception as exc:
        print(f"\n[!] RPC/NRPC test failed:")
        print(exc)


if __name__ == "__main__":
    main()