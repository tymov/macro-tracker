"""
Camera barcode scanner.

Implementation note: this uses st.camera_input (a single still photo)
decoded with pyzbar, rather than streamlit-webrtc's live video stream.
Live scanning would feel more like a native app, but streamlit-webrtc
needs a STUN/TURN setup to work reliably once deployed, which is a
separate infra decision. A still photo works with zero extra hosting
config and is a straightforward upgrade path to streamlit-webrtc later
if you want live scanning.

Requires the system library libzbar0 — see packages.txt.
"""

import streamlit as st
from PIL import Image


def render_barcode_scanner():
    """Renders a camera capture UI. Returns the decoded barcode
    string once a photo with a readable barcode is taken, else None."""

    try:
        from pyzbar.pyzbar import decode as zbar_decode
    except ImportError:
        st.info(
            "Barcode scanning needs the `pyzbar` package "
            "(and libzbar0) — see requirements.txt / packages.txt."
        )
        return None

    photo = st.camera_input(
        "Point your camera at the barcode",
        label_visibility="collapsed",
    )

    if photo is None:
        return None

    image = Image.open(photo)
    results = zbar_decode(image)

    if not results:
        st.warning("No barcode detected. Try moving closer or improving lighting.")
        return None

    code = results[0].data.decode("utf-8")
    st.success(f"Detected barcode: {code}")

    return code
