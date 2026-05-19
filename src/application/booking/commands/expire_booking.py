from dataclasses import dataclass


@dataclass(frozen=True)
class ExpireBookingCommand:
    """
    Command untuk menandai booking sebagai Expired.
    Dijalankan oleh System secara otomatis setelah payment deadline lewat.
    """
    booking_id: str