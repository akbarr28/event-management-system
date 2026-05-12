# event-management-system

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Clean Architecture Overview](#clean-architecture-overview)
- [How to Run](#how-to-run)
- [How to Configure PostgreSQL](#how-to-configure-postgresql)
- [How to Run Database Migration](#how-to-run-database-migration)
- [How to Run Tests](#how-to-run-tests)
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
event-ticketing-system/
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
│   │   │   ├── entities/               # (if any sub-entities)
│   │   │   ├── value_objects/          # BookingId, BookingStatus, etc.
│   │   │   ├── domain_services/        # Domain services for Booking
│   │   │   ├── domain_events/          # TicketReserved, BookingPaid, etc.
│   │   │   └── repositories/           # IBookingRepository interface
│   │   │
│   │   ├── ticket/
│   │   │   ├── aggregates/             # Ticket aggregate root
│   │   │   ├── entities/
│   │   │   ├── value_objects/          # TicketId, TicketCode, TicketStatus
│   │   │   ├── domain_services/        # Domain services for Ticket
│   │   │   ├── domain_events/          # TicketCheckedIn
│   │   │   └── repositories/           # ITicketRepository interface
│   │   │
│   │   ├── refund/
│   │   │   ├── aggregates/             # Refund aggregate root
│   │   │   ├── entities/
│   │   │   ├── value_objects/          # RefundId, RefundStatus, etc.
│   │   │   ├── domain_services/        # Domain services for Refund
│   │   │   ├── domain_events/          # RefundRequested, RefundApproved, etc.
│   │   │   └── repositories/           # IRefundRepository interface
│   │   │
│   │   └── shared/
│   │       ├── value_objects/          # Money, shared IDs
│   │       └── exceptions/             # Domain exceptions
│   │
│   ├── application/                    # Application Layer — use cases
│   │   ├── event/
│   │   │   ├── commands/               # CreateEvent, PublishEvent, CancelEvent, etc.
│   │   │   └── queries/                # GetAvailableEvents, GetEventDetail, etc.
│   │   │
│   │   ├── booking/
│   │   │   ├── commands/               # CreateBooking, PayBooking, ExpireBooking
│   │   │   └── queries/                # GetBookingDetail, etc.
│   │   │
│   │   ├── ticket/
│   │   │   ├── commands/               # CheckInTicket
│   │   │   └── queries/                # GetPurchasedTickets
│   │   │
│   │   ├── refund/
│   │   │   ├── commands/               # RequestRefund, ApproveRefund, etc.
│   │   │   └── queries/                # GetRefundDetail
│   │   │
│   │   └── shared/
│   │       ├── interfaces/             # IPaymentGateway, INotificationService, etc.
│   │       └── dtos/                   # Data Transfer Objects
│   │
│   ├── infrastructure/                 # Infrastructure Layer — external concerns
│   │   ├── database/
│   │   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   └── migrations/             # Alembic migration files
│   │   │
│   │   ├── repositories/               # PostgreSQL repository implementations
│   │   ├── services/
│   │   │   ├── payment/                # PaymentGateway implementation
│   │   │   ├── notification/           # NotificationService implementation
│   │   │   └── refund/                 # RefundPaymentService implementation
│   │   │
│   │   └── config/                     # DB connection, env config
│   │
│   ├── presentation/                   # Presentation Layer — HTTP interface
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── routers/            # FastAPI route handlers
│   │   │       └── schemas/            # Pydantic request/response schemas
│   │   └── middlewares/                # Auth, error handling middleware
│   │
│   └── main.py                         # FastAPI app entry point
│
├── tests/
│   ├── unit/
│   │   └── domain/
│   │       ├── event/                  # Unit tests for Event domain
│   │       ├── booking/                # Unit tests for Booking domain
│   │       ├── ticket/                 # Unit tests for Ticket domain
│   │       └── refund/                 # Unit tests for Refund domain
│   └── integration/                    # Integration tests
│
├── .env.example
├── .gitignore
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
git clone git@github.com:USERNAME/event-ticketing-system.git
cd event-ticketing-system

# 2. Buat dan aktifkan virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux / WSL / macOS
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy dan sesuaikan file environment
cp .env.example .env
# Edit .env dengan konfigurasi lokal kamu

# 5. Jalankan aplikasi
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi dapat diakses di: `http://localhost:8000`  
API docs (Swagger): `http://localhost:8000/docs`

---

## How to Configure PostgreSQL

```bash
# Masuk ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE event_ticketing_db;

# Buat user (opsional)
CREATE USER ticketing_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE event_ticketing_db TO ticketing_user;

\q
```

Lalu sesuaikan `DATABASE_URL` di file `.env`:

```
DATABASE_URL=postgresql+asyncpg://ticketing_user:yourpassword@localhost:5432/event_ticketing_db
```

---

## How to Run Database Migration

```bash
# Inisialisasi Alembic (hanya pertama kali)
alembic init src/infrastructure/database/migrations

# Buat file migrasi baru
alembic revision --autogenerate -m "initial schema"

# Jalankan migrasi
alembic upgrade head

# Rollback migrasi (jika perlu)
alembic downgrade -1
```

---

## How to Run Tests

```bash
# Jalankan semua unit test
pytest tests/unit/ -v

# Jalankan test untuk domain tertentu
pytest tests/unit/domain/event/ -v
pytest tests/unit/domain/booking/ -v
pytest tests/unit/domain/ticket/ -v
pytest tests/unit/domain/refund/ -v

# Jalankan dengan coverage report
pytest tests/unit/ --cov=src/domain --cov-report=term-missing
```

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
- Total harga = harga satuan tiket × jumlah tiket.
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
- Tiket dari event yang dibatalkan harus berstatus `CANCELLED`.

**BR-T02 — Check In Ticket**
- Check-in hanya dapat dilakukan untuk event yang sesuai dengan tiket.
- Tiket harus berstatus `ACTIVE` untuk dapat di-check-in.
- Tiket yang sudah di-check-in tidak dapat digunakan lagi.
- Check-in hanya dapat dilakukan pada hari event atau dalam jangka waktu check-in yang diizinkan.
- Setelah check-in berhasil, status tiket berubah menjadi `CHECKED_IN`.
- Sistem akan memunculkan domain event `TicketCheckedIn`.

**BR-T03 — Reject Invalid Check-in**
- Jika kode tiket tidak ditemukan → tampilkan pesan tiket tidak valid.
- Jika tiket sudah pernah di-check-in → tampilkan pesan tiket sudah digunakan.
- Jika tiket milik event lain → tampilkan pesan tiket tidak sesuai event.
- Jika event dibatalkan → tampilkan pesan event telah dibatalkan.
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

> Akan diperbarui seiring perkembangan implementasi.

| User Story | Description | Status |
|------------|-------------|--------|
| US-01 | Create Event | 🔲 Pending |
| US-02 | Publish Event | 🔲 Pending |
| US-03 | Cancel Event | 🔲 Pending |
| US-04 | Create Ticket Category | 🔲 Pending |
| US-05 | Disable Ticket Category | 🔲 Pending |
| US-06 | View Available Events | 🔲 Pending |
| US-07 | View Event Details | 🔲 Pending |
| US-08 | Create Ticket Booking | 🔲 Pending |
| US-09 | Calculate Booking Total Price | 🔲 Pending |
| US-10 | Pay Booking | 🔲 Pending |
| US-11 | Expire Booking | 🔲 Pending |
| US-12 | View Purchased Tickets | 🔲 Pending |
| US-13 | Check In Ticket | 🔲 Pending |
| US-14 | Reject Invalid Ticket Check-in | 🔲 Pending |
| US-15 | Request Refund | 🔲 Pending |
| US-16 | Approve Refund | 🔲 Pending |
| US-17 | Reject Refund | 🔲 Pending |
| US-18 | Mark Refund as Paid Out | 🔲 Pending |
| US-19 | View Event Sales Report | 🔲 Pending |
| US-20 | View Event Participants | 🔲 Pending |

---

## Implemented Domain Events

> Akan diperbarui seiring perkembangan implementasi.

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

> Akan diperbarui seiring perkembangan implementasi.

| Interface | Description |
|-----------|-------------|
| `IPaymentGateway` | Memproses pembayaran booking melalui payment gateway eksternal |
| `INotificationService` | Mengirim notifikasi email atau WhatsApp ke customer |
| `IRefundPaymentService` | Memproses pencairan refund ke rekening customer melalui bank service |