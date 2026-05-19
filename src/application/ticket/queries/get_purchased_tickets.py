from dataclasses import dataclass


@dataclass(frozen=True)
class GetPurchasedTicketsQuery:
    """
    Query untuk mengambil tiket yang sudah dibeli customer.
    Digunakan oleh Customer untuk melihat tiket mereka.
    """
    customer_id: str