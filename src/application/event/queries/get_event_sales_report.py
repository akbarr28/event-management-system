from dataclasses import dataclass


@dataclass(frozen=True)
class GetEventSalesReportQuery:
    """
    Query untuk mengambil laporan penjualan event.
    Digunakan oleh Event Organizer untuk melihat performa penjualan tiket.
    """
    event_id: str