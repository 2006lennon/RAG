from impacket.dcerpc.v5 import nrpc
import inspect


def check_function(name):
    obj = getattr(nrpc, name, None)

    if obj is None:
        print(f"[MISSING] {name}")
        return

    print(f"[OK] {name}")

    try:
        print("  signature:", inspect.signature(obj))
    except Exception:
        print("  signature: N/A")


def check_class(name):
    obj = getattr(nrpc, name, None)

    if obj is None:
        print(f"[MISSING] {name}")
        return

    print(f"[OK] {name}")

    if hasattr(obj, "structure"):
        print("  structure:", obj.structure)


print("=== Impacket NRPC API Validation ===")

check_function("hNetrServerReqChallenge")
check_class("NetrServerReqChallenge")
check_class("NETLOGON_CREDENTIAL")
check_class("NETLOGON_AUTHENTICATOR")

print("\nNRPC UUID:")
print(nrpc.MSRPC_UUID_NRPC)