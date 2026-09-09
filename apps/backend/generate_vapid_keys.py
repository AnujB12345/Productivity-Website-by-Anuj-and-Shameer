# generate_vapid_keys.py
from py_vapid import Vapid
import base64

vapid = Vapid()
vapid.generate_keys()

vapid.save_key("private_key.pem")
vapid.save_public_key("public_key.pem")

# This produces the same "applicationServerKey" string the CLI prints —
# the raw EC public key point, base64url-encoded with no padding.
raw_public = vapid.public_key.public_bytes(
    encoding=__import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.X962,
    format=__import__("cryptography.hazmat.primitives.serialization", fromlist=["PublicFormat"]).PublicFormat.UncompressedPoint,
)
application_server_key = base64.urlsafe_b64encode(raw_public).rstrip(b"=").decode("utf-8")

print("Saved private_key.pem and public_key.pem in the current folder.")
print()
print("VAPID_PUBLIC_KEY (applicationServerKey) =")
print(application_server_key)