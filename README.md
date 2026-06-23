# Event Ticketing & Booking System

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Clean Architecture Overview](#clean-architecture-overview)
- [How to Run](#how-to-run)
- [How to Configure PostgreSQL](#how-to-configure-postgresql)
- [How to Run Database Migration](#how-to-run-database-migration)
- [How to Run Tests](#how-to-run-tests)
- [API Documentation](#api-documentation)
- [Business Rules](#business-rules)
- [Ubiquitous Language Glossary](#ubiquitous-language-glossary)
- [Implemented User Stories](#implemented-user-stories)
- [Implemented Domain Events](#implemented-domain-events)
- [Implemented Application Service Interfaces](#implemented-application-service-interfaces)

---

## Tech Stack

| Component     | Technology                  |
|---------------|-----------------------------|
| Language      | Python 3.11+                |
| Framework     | FastAPI                     |
| Database      | PostgreSQL                  |
| ORM           | SQLAlchemy (async)          |
| Migration     | Alembic                     |
| Architecture  | Clean Architecture + DDD    |
| Testing       | Pytest + pytest-asyncio     |

---

## Project Structure

```
event-management-system/
│
├── src/
│   ├── domain/                         # Domain Layer — core business logic
│   │   ├── event/
│   │   │   ├── aggregates/             # Event aggregate root
│   │   │   ├── entities/               # TicketCategory entity
│   │   │   ├── value_objects/          # EventId, EventStatus, etc.
│   │   │   ├── domain_services/        # Domain services for Event
│   │   │   ├── domain_events/          # EventCreated, EventPublished, etc.
│   │   │   └── repositories/           # IEventRepository interface
│   │   │
│   │   ├── booking/
│   │   │   ├── aggregates/             # Booking aggregate root
│   │   │   ├── value_objects/          # BookingId, BookingStatus, etc.
│   │   │   ├── domain_services/        # BookingDomainService
│   │   │   ├── domain_events/          # TicketReserved, BookingPaid, etc.
│   │   │   └── repositories/           # IBookingRepository interface
│   │   │
│   │   ├── ticket/
│   │   │   ├── entities/               # Ticket entity
│   │   │   ├── value_objects/          # TicketId, TicketCode, TicketStatus
│   │   │   ├── domain_events/          # TicketCheckedIn
│   │   │   └── repositories/           # ITicketRepository interface
│   │   │
│   │   ├── refund/
│   │   │   ├── aggregates/             # Refund aggregate root
│   │   │   ├── value_objects/          # RefundId, RefundStatus, etc.
│   │   │   ├── domain_services/        # RefundDomainService
│   │   │   ├── domain_events/          # RefundRequested, RefundApproved, etc.
│   │   │   └── repositories/           # IRefundRepository interface
│   │   │
│   │   └── shared/
│   │       ├── value_objects/          # Money
│   │       └── exceptions/             # DomainException
│   │
│   ├── application/                    # Application Layer — use cases
│   │   ├── event/
│   │   │   ├── commands/               # CreateEvent, PublishEvent, CancelEvent, etc.
│   │   │   └── queries/                # GetAvailableEvents, GetEventDetail, etc.
│   │   ├── booking/
│   │   │   └── commands/               # CreateBooking, PayBooking, ExpireBooking
│   │   ├── ticket/
│   │   │   ├── commands/               # CheckInTicket
│   │   │   └── queries/                # GetPurchasedTickets
│   │   ├── refund/
│   │   │   └── commands/               # RequestRefund, ApproveRefund, etc.
│   │   └── shared/
│   │       ├── interfaces/             # IPaymentGateway, INotificationService, etc.
│   │       └── dtos/                   # Data Transfer Objects
│   │
│   ├── infrastructure/                 # Infrastructure Layer — external concerns
│   │   ├── database/
│   │   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   └── connection.py           # DB engine + session factory
│   │   ├── repositories/               # PostgreSQL repository implementations
│   │   ├── services/
│   │   │   ├── payment/                # ConsolePaymentGateway
│   │   │   ├── notification/           # ConsoleNotificationService
│   │   │   └── refund/                 # ConsoleRefundPaymentService
│   │   └── config/                     # Settings from .env
│   │
│   ├── presentation/                   # Presentation Layer — HTTP interface
│   │   └── api/
│   │       └── v1/
│   │           └── routers/            # FastAPI route handlers
│   │
│   └── main.py                         # FastAPI app entry point
│
├── migrations/                         # Alembic migration scripts
│   └── versions/
├── tests/
│   └── unit/
│       └── domain/
│           ├── event/
│           ├── booking/
│           ├── ticket/
│           └── refund/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Clean Architecture Overview

```
┌──────────────────────────────────────────┐
│           Presentation Layer             │  ← FastAPI routers, Pydantic schemas
├──────────────────────────────────────────┤
│           Infrastructure Layer           │  ← PostgreSQL, external services
├──────────────────────────────────────────┤
│           Application Layer              │  ← Commands, Queries, DTOs, Interfaces
├──────────────────────────────────────────┤
│             Domain Layer                 │  ← Aggregates, Entities, Value Objects
│        (no external dependencies)        │     Domain Events, Repository Interfaces
└──────────────────────────────────────────┘
```

Dependency rule: setiap layer hanya boleh bergantung ke layer yang lebih dalam. Domain layer tidak boleh bergantung pada layer manapun.

---

## How to Run

```bash
# 1. Clone repository
git clone git@github.com:USERNAME/event-management-system.git
cd event-management-system

# 2. Buat dan aktifkan virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux / WSL / macOS
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy dan sesuaikan file environment
cp .env.example .env
# Edit .env dengan konfigurasi lokal kamu

# 5. Start PostgreSQL (WSL)
sudo service postgresql start

# 6. Jalankan migrasi database
python -m alembic upgrade head

# 7. Jalankan aplikasi
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi dapat diakses di: `http://localhost:8000`  
API docs (Swagger UI): `http://localhost:8000/docs`  
API docs (ReDoc): `http://localhost:8000/redoc`

---

## How to Configure PostgreSQL

```bash
# Start PostgreSQL (WSL)
sudo service postgresql start

# Masuk ke PostgreSQL
sudo -u postgres psql

# Buat database
CREATE DATABASE event_db;
ALTER USER postgres PASSWORD 'password';
\q
```

Sesuaikan `DATABASE_URL` di file `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/event_db
DATABASE_ECHO=false
```

---

## How to Run Database Migration

```bash
# Jalankan semua migrasi
python -m alembic upgrade head

# Cek status migrasi saat ini
python -m alembic current

# Lihat riwayat migrasi
python -m alembic history

# Rollback satu langkah
python -m alembic downgrade -1

# Rollback ke awal
python -m alembic downgrade base
```

---

## How to Run Tests

```bash
# Jalankan semua unit test
pytest tests/unit/ -v

# Jalankan test per domain
pytest tests/unit/domain/event/ -v
pytest tests/unit/domain/booking/ -v
pytest tests/unit/domain/ticket/ -v
pytest tests/unit/domain/refund/ -v

# Jalankan dengan coverage report
pytest tests/unit/ --cov=src/domain --cov-report=term-missing
```

---

## API Documentation

Swagger UI tersedia di `http://localhost:8000/docs` setelah aplikasi dijalankan.

**Base URL:** `http://localhost:8000/api/v1`

---

### Events

#### US-01 — Create Event
```
POST /api/v1/events
```
Request body:
```json
{
  "name": "ITS Tech Festival 2025",
  "description": "Annual technology festival at ITS.",
  "start_date": "2025-12-01T08:00:00",
  "end_date": "2025-12-02T17:00:00",
  "location": "Surabaya, ITS Campus",
  "maximum_capacity": 500,
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
Response `201`:
```json
{
  "id": "uuid",
  "name": "ITS Tech Festival 2025",
  "status": "DRAFT",
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### US-02 — Publish Event
```
POST /api/v1/events/{event_id}/publish
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
Response `200`: Event berhasil dipublish, status berubah menjadi `PUBLISHED`.

---

#### US-03 — Cancel Event
```
POST /api/v1/events/{event_id}/cancel
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
Response `200`: Event berhasil dibatalkan, status berubah menjadi `CANCELLED`.

---

#### US-04 — Create Ticket Category
```
POST /api/v1/events/{event_id}/ticket-categories
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Regular",
  "price": 150000,
  "currency": "IDR",
  "quota": 100,
  "sales_start_date": "2025-11-01T00:00:00",
  "sales_end_date": "2025-11-30T23:59:59"
}
```
Response `201`: Ticket category berhasil ditambahkan ke event.

---

#### US-05 — Disable Ticket Category
```
POST /api/v1/events/{event_id}/ticket-categories/{ticket_category_id}/disable
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
Response `200`: Ticket category berhasil dinonaktifkan.

---

#### US-06 — View Available Events
```
GET /api/v1/events
GET /api/v1/events?filter_date=2025-12-01T00:00:00&filter_location=Surabaya
```
Query parameters (opsional):
- `filter_date` — filter by tanggal event (format: ISO 8601)
- `filter_location` — filter by lokasi event (case-insensitive)

Response `200`:
```json
[
  {
    "id": "uuid",
    "name": "ITS Tech Festival 2025",
    "description": "Annual technology festival at ITS.",
    "start_date": "2025-12-01T08:00:00",
    "end_date": "2025-12-02T17:00:00",
    "location": "Surabaya, ITS Campus",
    "organizer_id": "uuid",
    "status": "PUBLISHED",
    "lowest_price": 150000,
    "lowest_price_currency": "IDR"
  }
]
```

---

#### US-07 — View Event Detail
```
GET /api/v1/events/{event_id}
```
Response `200`:
```json
{
  "id": "uuid",
  "name": "ITS Tech Festival 2025",
  "description": "Annual technology festival at ITS.",
  "start_date": "2025-12-01T08:00:00",
  "end_date": "2025-12-02T17:00:00",
  "location": "Surabaya, ITS Campus",
  "organizer_id": "uuid",
  "status": "PUBLISHED",
  "maximum_capacity": 500,
  "ticket_categories": [
    {
      "id": "uuid",
      "name": "Regular",
      "price": 150000,
      "currency": "IDR",
      "quota": 100,
      "remaining_quota": 85,
      "sales_start_date": "2025-11-01T00:00:00",
      "sales_end_date": "2025-11-30T23:59:59",
      "status": "ACTIVE",
      "display_status": "Available"
    }
  ]
}
```
Nilai `display_status` yang mungkin: `Available`, `Coming Soon`, `Sales Closed`, `Sold Out`, `Inactive`.

---

#### US-19 — View Event Sales Report
```
GET /api/v1/events/{event_id}/sales-report
```
Response `200`:
```json
{
  "event_id": "uuid",
  "event_name": "ITS Tech Festival 2025",
  "total_pending_payment": 5,
  "total_paid": 80,
  "total_expired": 10,
  "total_refunded": 2,
  "total_revenue_amount": 12000000,
  "total_revenue_currency": "IDR",
  "tickets_sold_per_category": [
    {
      "category_name": "Regular",
      "tickets_sold": 80
    }
  ]
}
```

---

#### US-20 — View Event Participants
```
GET /api/v1/events/{event_id}/participants
```
Response `200`:
```json
[
  {
    "customer_name": "uuid-customer",
    "ticket_category_name": "Regular",
    "ticket_code": "ABC123DEF456",
    "is_checked_in": false
  }
]
```

---

### Bookings

#### US-08 — Create Booking
```
POST /api/v1/bookings
```
Request body:
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440001",
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "ticket_category_id": "550e8400-e29b-41d4-a716-446655440003",
  "quantity": 2
}
```
Response `201`:
```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "event_id": "uuid",
  "ticket_category_id": "uuid",
  "quantity": 2,
  "unit_price": 150000,
  "total_price": 300000,
  "currency": "IDR",
  "status": "PENDING_PAYMENT",
  "payment_deadline": "2025-11-01T10:15:00"
}
```

---

#### US-09 — Calculate Booking Total Price
```
GET /api/v1/bookings/{booking_id}/total-price
```
Response `200`:
```json
{
  "booking_id": "uuid",
  "unit_price": "150000",
  "quantity": 2,
  "total_price": "300000",
  "currency": "IDR"
}
```

---

#### US-10 — Pay Booking
```
POST /api/v1/bookings/{booking_id}/pay
```
Request body:
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440001",
  "payment_amount": 300000,
  "currency": "IDR"
}
```
Response `200`: List tiket yang diterbitkan setelah pembayaran berhasil:
```json
[
  {
    "id": "uuid",
    "booking_id": "uuid",
    "event_id": "uuid",
    "ticket_category_id": "uuid",
    "customer_id": "uuid",
    "ticket_code": "ABC123DEF456",
    "status": "ACTIVE"
  }
]
```

---

#### US-11 — Expire Booking
```
POST /api/v1/bookings/{booking_id}/expire
```
Response `200`: Booking berhasil di-expire, quota tiket dilepas kembali.

---

### Tickets

#### US-12 — View Purchased Tickets
```
GET /api/v1/tickets/my-tickets?customer_id={customer_id}
```
Query parameters:
- `customer_id` — UUID customer (wajib)

Response `200`:
```json
[
  {
    "id": "uuid",
    "booking_id": "uuid",
    "event_id": "uuid",
    "ticket_category_id": "uuid",
    "customer_id": "uuid",
    "ticket_code": "ABC123DEF456",
    "status": "ACTIVE"
  }
]
```

---

#### US-13 & US-14 — Check In Ticket / Reject Invalid Check-in
```
POST /api/v1/tickets/check-in
```
Request body:
```json
{
  "ticket_code": "ABC123DEF456",
  "event_id": "550e8400-e29b-41d4-a716-446655440002"
}
```
Response `200` (berhasil):
```json
{
  "message": "Ticket checked in successfully."
}
```
Response `422` (rejection scenarios US-14):
```json
{ "detail": "Ticket is invalid. Ticket code not found." }
{ "detail": "Ticket has already been checked in." }
{ "detail": "Ticket does not match the event." }
{ "detail": "Event has been cancelled." }
{ "detail": "Cancelled ticket cannot be checked in." }
{ "detail": "Check-in is only allowed on the event day." }
```

---

### Refunds

#### US-15 — Request Refund
```
POST /api/v1/refunds/bookings/{booking_id}/refund
```
Request body:
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440001"
}
```
Response `201`:
```json
{
  "id": "uuid",
  "booking_id": "uuid",
  "customer_id": "uuid",
  "amount": 300000,
  "currency": "IDR",
  "status": "REQUESTED",
  "rejection_reason": null,
  "payment_reference": null
}
```

---

#### US-16 — Approve Refund
```
POST /api/v1/refunds/{refund_id}/approve
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```
Response `200`: Refund disetujui. Tiket terkait dibatalkan, booking ditandai `REFUNDED`.

---

#### US-17 — Reject Refund
```
POST /api/v1/refunds/{refund_id}/reject
```
Request body:
```json
{
  "organizer_id": "550e8400-e29b-41d4-a716-446655440000",
  "rejection_reason": "Tiket sudah digunakan sebelum event dibatalkan."
}
```
Response `200`: Refund ditolak. Booking tetap `PAID`, tiket tetap `ACTIVE`.

---

#### US-18 — Mark Refund as Paid Out
```
POST /api/v1/refunds/{refund_id}/paid-out
```
Request body:
```json
{
  "payment_reference": "TRX-20251201-ABC123"
}
```
Response `200`: Refund ditandai sebagai `PAID_OUT`, payment reference tercatat.

---

## Business Rules

### Event Management

**BR-E01 — Create Event**
- Event hanya dapat dibuat oleh Event Organizer yang sudah terautentikasi.
- `end_date` tidak boleh lebih awal dari `start_date`.
- `maximum_capacity` harus lebih besar dari nol.
- Event yang baru dibuat selalu berstatus `DRAFT`.
- Sistem akan memunculkan domain event `EventCreated` setelah event berhasil dibuat.

**BR-E02 — Publish Event**
- Event hanya dapat dipublish jika memiliki minimal satu ticket category dengan status `ACTIVE`.
- Total quota seluruh ticket category tidak boleh melebihi `maximum_capacity` event.
- Hanya event berstatus `DRAFT` yang dapat dipublish menjadi `PUBLISHED`.
- Event berstatus `CANCELLED` tidak dapat dipublish.
- Sistem akan memunculkan domain event `EventPublished`.

**BR-E03 — Cancel Event**
- Hanya event berstatus `PUBLISHED` yang dapat dibatalkan.
- Event berstatus `COMPLETED` tidak dapat dibatalkan.
- Ketika event dibatalkan, semua ticket category tidak dapat lagi dibeli.
- Semua booking yang sudah `PAID` harus ditandai memerlukan refund.
- Sistem akan memunculkan domain event `EventCancelled`.

---

### Ticket Category Management

**BR-TC01 — Create Ticket Category**
- Setiap ticket category harus memiliki nama, harga, quota, tanggal mulai jual, dan tanggal akhir jual.
- Harga tiket tidak boleh negatif (minimal 0).
- Quota harus lebih besar dari nol.
- Tanggal akhir jual harus sebelum atau sama dengan tanggal mulai event.
- Total quota semua ticket category tidak boleh melebihi `maximum_capacity` event.
- Sistem akan memunculkan domain event `TicketCategoryCreated`.

**BR-TC02 — Disable Ticket Category**
- Ticket category hanya dapat dinonaktifkan jika event belum berstatus `COMPLETED`.
- Ticket category yang sudah memiliki booking tetap disimpan untuk keperluan histori.
- Customer tidak dapat membeli tiket dari ticket category yang berstatus `INACTIVE`.
- Sistem akan memunculkan domain event `TicketCategoryDisabled`.

---

### Booking

**BR-B01 — Create Booking**
- Booking hanya dapat dibuat untuk event berstatus `PUBLISHED`.
- Booking hanya dapat dibuat untuk ticket category berstatus `ACTIVE`.
- Booking hanya dapat dibuat dalam periode penjualan ticket category.
- Jumlah tiket harus lebih dari nol.
- Jumlah tiket tidak boleh melebihi sisa quota ticket category.
- Satu customer hanya boleh memiliki satu booking aktif untuk event yang sama.
- Booking yang baru dibuat selalu berstatus `PENDING_PAYMENT`.
- Booking memiliki batas waktu pembayaran (payment deadline), yaitu 15 menit setelah dibuat.
- Sistem akan memunculkan domain event `TicketReserved`.

**BR-B02 — Calculate Booking Total Price**
- Total harga = harga satuan tiket x jumlah tiket.
- Jika ada service fee, service fee ditambahkan ke total harga.
- Total harga tidak boleh bernilai negatif.
- Total harga direpresentasikan menggunakan value object `Money`.

**BR-B03 — Pay Booking**
- Booking hanya dapat dibayar jika berstatus `PENDING_PAYMENT`.
- Booking tidak dapat dibayar jika payment deadline sudah terlewat.
- Jumlah pembayaran harus sama dengan total harga booking.
- Setelah pembayaran berhasil, status booking berubah menjadi `PAID`.
- Setelah booking dibayar, sistem menerbitkan tiket dengan kode tiket unik.
- Sistem akan memunculkan domain event `BookingPaid`.

**BR-B04 — Expire Booking**
- Booking berstatus `PENDING_PAYMENT` berubah menjadi `EXPIRED` setelah payment deadline terlewat.
- Booking berstatus `PAID` tidak dapat di-expire.
- Ketika booking expired, quota tiket yang sebelumnya direservasi dilepaskan kembali.
- Sistem akan memunculkan domain event `BookingExpired`.

---

### Ticket & Check-in

**BR-T01 — View Purchased Tickets**
- Customer hanya dapat melihat tiket dari booking berstatus `PAID`.
- Setiap tiket memiliki kode tiket yang unik.
- Setiap tiket memiliki salah satu status: `ACTIVE`, `CHECKED_IN`, atau `CANCELLED`.

**BR-T02 — Check In Ticket**
- Check-in hanya dapat dilakukan untuk event yang sesuai dengan tiket.
- Tiket harus berstatus `ACTIVE` untuk dapat di-check-in.
- Tiket yang sudah di-check-in tidak dapat digunakan lagi.
- Check-in hanya dapat dilakukan pada hari event.
- Setelah check-in berhasil, status tiket berubah menjadi `CHECKED_IN`.
- Sistem akan memunculkan domain event `TicketCheckedIn`.

**BR-T03 — Reject Invalid Check-in**
- Jika kode tiket tidak ditemukan, tampilkan pesan tiket tidak valid.
- Jika tiket sudah pernah di-check-in, tampilkan pesan tiket sudah digunakan.
- Jika tiket milik event lain, tampilkan pesan tiket tidak sesuai event.
- Jika event dibatalkan, tampilkan pesan event telah dibatalkan.
- Status tiket tidak boleh berubah jika check-in gagal.

---

### Refund Management

**BR-R01 — Request Refund**
- Refund hanya dapat diminta untuk booking berstatus `PAID`.
- Refund tidak dapat diminta jika ada tiket dari booking yang sudah di-check-in.
- Refund hanya dapat diminta sebelum refund deadline.
- Jika event dibatalkan, refund otomatis diizinkan.
- Sistem akan memunculkan domain event `RefundRequested`.

**BR-R02 — Approve Refund**
- Refund hanya dapat disetujui jika berstatus `REQUESTED`.
- Ketika refund disetujui, statusnya berubah menjadi `APPROVED`.
- Tiket terkait berubah menjadi `CANCELLED`.
- Booking terkait berubah menjadi `REFUNDED`.
- Sistem akan memunculkan domain event `RefundApproved`.

**BR-R03 — Reject Refund**
- Refund hanya dapat ditolak jika berstatus `REQUESTED`.
- Alasan penolakan wajib diisi.
- Ketika refund ditolak, statusnya berubah menjadi `REJECTED`.
- Booking terkait tetap berstatus `PAID`.
- Tiket terkait tetap berstatus `ACTIVE` jika belum dibatalkan.
- Sistem akan memunculkan domain event `RefundRejected`.

**BR-R04 — Mark Refund as Paid Out**
- Refund hanya dapat ditandai sebagai paid out jika berstatus `APPROVED`.
- Payment reference wajib dicatat.
- Ketika refund paid out, statusnya berubah menjadi `PAID_OUT`.
- Refund yang sudah paid out tidak dapat diubah lagi.
- Sistem akan memunculkan domain event `RefundPaidOut`.

---

## Ubiquitous Language Glossary

| Term | Meaning |
|------|---------|
| **Event** | Kegiatan yang diorganisir oleh Event Organizer dan dihadiri oleh Customer. |
| **Event Organizer** | Pengguna yang membuat dan mengelola event. |
| **Customer** | Pengguna yang memesan dan membeli tiket. |
| **Gate Officer** | Pengguna yang memvalidasi tiket saat check-in berlangsung. |
| **System Admin** | Pengguna dengan akses administratif untuk memproses refund payout dan memonitor sistem. |
| **Ticket Category** | Jenis tiket dalam suatu event, seperti Regular, VIP, atau Early Bird. |
| **Quota** | Jumlah maksimum tiket yang tersedia dalam satu ticket category. |
| **Remaining Quota** | Sisa tiket yang masih tersedia untuk dibeli dalam suatu ticket category. |
| **Booking** | Reservasi sementara tiket sebelum pembayaran diselesaikan. |
| **Pending Payment** | Status booking yang menandakan pembayaran belum dilakukan. |
| **Paid** | Status booking yang menandakan pembayaran sudah selesai. |
| **Expired** | Status booking yang menandakan batas waktu pembayaran telah terlewat. |
| **Refunded** | Status booking yang menandakan refund sudah diproses. |
| **Payment Deadline** | Batas waktu untuk menyelesaikan pembayaran setelah booking dibuat (15 menit). |
| **Ticket** | Bukti kehadiran yang diterbitkan setelah booking berhasil dibayar. |
| **Ticket Code** | Kode unik yang digunakan untuk mengidentifikasi dan memvalidasi tiket. |
| **Active** | Status tiket yang menandakan tiket valid dan belum digunakan. |
| **Checked In** | Status tiket yang menandakan pemilik tiket sudah memasuki venue event. |
| **Cancelled** | Status tiket yang menandakan tiket tidak berlaku lagi. |
| **Check-in** | Proses validasi tiket ketika peserta memasuki venue event. |
| **Sales Period** | Periode waktu di mana suatu ticket category dapat dibeli oleh customer. |
| **Refund** | Proses pengembalian uang kepada customer. |
| **Refund Deadline** | Batas waktu maksimal customer dapat mengajukan refund. |
| **Money** | Value object yang merepresentasikan jumlah uang beserta mata uangnya. |
| **Domain Event** | Kejadian penting dalam domain bisnis yang telah terjadi dan perlu dicatat/diproses. |
| **Aggregate** | Kumpulan entity dan value object yang diperlakukan sebagai satu unit konsistensi. |
| **Aggregate Root** | Entity utama dalam aggregate yang menjadi satu-satunya pintu masuk untuk mengubah state aggregate. |
| **Repository** | Abstraksi untuk menyimpan dan mengambil aggregate dari storage. |
| **Value Object** | Objek yang diidentifikasi berdasarkan nilainya, bukan identitasnya. Bersifat immutable. |
| **Draft** | Status event yang baru dibuat dan belum dipublish. |
| **Published** | Status event yang sudah dipublish dan dapat dilihat serta dibeli tiketnya oleh customer. |
| **Completed** | Status event yang sudah selesai dilaksanakan. |

---

## Implemented User Stories

| User Story | Description | Status |
|------------|-------------|--------|
| US-01 | Create Event | ✅ Done |
| US-02 | Publish Event | ✅ Done |
| US-03 | Cancel Event | ✅ Done |
| US-04 | Create Ticket Category | ✅ Done |
| US-05 | Disable Ticket Category | ✅ Done |
| US-06 | View Available Events | ✅ Done |
| US-07 | View Event Details | ✅ Done |
| US-08 | Create Ticket Booking | ✅ Done |
| US-09 | Calculate Booking Total Price | ✅ Done |
| US-10 | Pay Booking | ✅ Done |
| US-11 | Expire Booking | ✅ Done |
| US-12 | View Purchased Tickets | ✅ Done |
| US-13 | Check In Ticket | ✅ Done |
| US-14 | Reject Invalid Ticket Check-in | ✅ Done |
| US-15 | Request Refund | ✅ Done |
| US-16 | Approve Refund | ✅ Done |
| US-17 | Reject Refund | ✅ Done |
| US-18 | Mark Refund as Paid Out | ✅ Done |
| US-19 | View Event Sales Report | ✅ Done |
| US-20 | View Event Participants | ✅ Done |

---

## Implemented Domain Events

| Domain Event | Raised By | Trigger |
|--------------|-----------|---------|
| `EventCreated` | Event | Event berhasil dibuat |
| `EventPublished` | Event | Event dipublish |
| `EventCancelled` | Event | Event dibatalkan |
| `TicketCategoryCreated` | TicketCategory | Ticket category dibuat |
| `TicketCategoryDisabled` | TicketCategory | Ticket category dinonaktifkan |
| `TicketReserved` | Booking | Booking berhasil dibuat |
| `BookingPaid` | Booking | Pembayaran booking berhasil |
| `BookingExpired` | Booking | Booking melewati payment deadline |
| `TicketCheckedIn` | Ticket | Tiket berhasil di-check-in |
| `RefundRequested` | Refund | Customer mengajukan refund |
| `RefundApproved` | Refund | Organizer menyetujui refund |
| `RefundRejected` | Refund | Organizer menolak refund |
| `RefundPaidOut` | Refund | Admin menandai refund sebagai paid out |

---

## Implemented Application Service Interfaces

| Interface | Implementation | Description |
|-----------|---------------|-------------|
| `IPaymentGateway` | `ConsolePaymentGateway` | Memproses pembayaran booking melalui payment gateway eksternal |
| `INotificationService` | `ConsoleNotificationService` | Mengirim notifikasi email atau WhatsApp ke customer |
| `IRefundPaymentService` | `ConsoleRefundPaymentService` | Memproses pencairan refund ke rekening customer melalui bank service |