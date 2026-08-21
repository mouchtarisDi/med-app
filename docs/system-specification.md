# System Specification v1.0

## Medical Practice Management System

**Version:** 1.0
**Status:** Initial Specification
**Project Type:** Web-based Medical Practice Management System
**Architecture:** Multi-tenant SaaS
**Backend:** Python / FastAPI
**Frontend:** React / TypeScript
**Database:** PostgreSQL
**ORM:** SQLAlchemy
**Database Migrations:** Alembic
**Infrastructure:** Docker

---

# 1. Project Overview

The project concerns the design and development of a web-based application for the management of small and medium-sized medical practices.

The application aims to centralize the main daily operations of a medical practice, including patient management, appointment scheduling, medical records, staff management, payments, notifications and basic analytics.

The system is designed as a **multi-tenant application**, allowing multiple independent medical practices to use the same platform while keeping their data logically isolated.

A secondary goal of the project is the introduction of intelligent functionality that can assist medical staff with tasks such as appointment management, no-show risk estimation and scheduling recommendations.

The application is not intended to replace specialized hospital information systems or full Electronic Health Record (EHR) platforms. Its focus is simplicity, usability and the requirements of smaller medical practices.

---

# 2. System Goals

The main goals of the system are:

* Centralize patient and appointment information.
* Reduce manual administrative work.
* Provide simple appointment scheduling and management.
* Provide doctors with structured access to patient medical records.
* Allow secretaries to manage the daily operation of the medical practice.
* Allow patients to access limited appointment functionality without maintaining a permanent account.
* Record payments for internal statistics and reporting.
* Provide useful operational statistics to the practice owner.
* Introduce automated and intelligent features that assist with scheduling and appointment management.
* Maintain clear separation of data between different medical practices.
* Provide a scalable architecture that can be extended in the future.

---

# 3. Target Users

The main target users are:

* Small medical practices
* Independent doctors
* Medical practices employing one or more secretaries
* Small practices with multiple doctors

The system is primarily intended for environments where the doctor may also be the owner of the practice.

---

# 4. Actors and Roles

The system defines four main actors.

## 4.1 Owner

The Owner has administrative control over a medical practice.

An Owner may also be a Doctor.

Main permissions include:

* Manage practice information.
* Manage staff.
* Manage doctors and secretaries.
* Access patients.
* Access appointments.
* Access financial statistics.
* Access operational statistics.
* Configure practice-level settings.

---

## 4.2 Doctor

A Doctor is a staff user associated with a medical practice.

Main permissions include:

* View assigned appointments.
* Access patient information.
* Create and update medical records.
* Access patient medical history.
* Create prescriptions where supported.
* View relevant notifications.
* Manage appointment-related information where permitted.

A Doctor may simultaneously hold the Owner role.

---

## 4.3 Secretary

A Secretary manages the administrative workflow of the medical practice.

Main permissions include:

* Register patients.
* Update basic patient information.
* Create appointments.
* Reschedule appointments.
* Cancel appointments.
* View doctors' schedules.
* Record payments.
* Manage administrative appointment information.

Secretaries must not automatically receive access to sensitive clinical information unless explicitly permitted by the authorization model.

---

## 4.4 Patient

A Patient is **not a normal authenticated User of the main application**.

Patients do not maintain usernames or passwords.

Instead, limited access is provided through the Patient Portal using:

**AMKA + One-Time Password (OTP)**

The Patient Portal provides access only to specifically authorized functionality.

---

# 5. Multi-Tenant Architecture

The application shall follow a multi-tenant architecture.

Each medical practice represents an independent tenant.

Conceptually:

```text
Application
│
├── Clinic A
│   ├── Staff
│   ├── Doctors
│   ├── Patients
│   ├── Appointments
│   └── Medical Records
│
├── Clinic B
│   ├── Staff
│   ├── Doctors
│   ├── Patients
│   ├── Appointments
│   └── Medical Records
│
└── Clinic C
    └── ...
```

Data belonging to one clinic must not be accessible by users belonging exclusively to another clinic.

Tenant isolation shall therefore be enforced at the application and data-access layers.

The first version does not require implementation of subscription billing or automated SaaS payment plans.

However, the architecture should allow such functionality to be introduced later without requiring a complete redesign.

---

# 6. Patient Portal

The Patient Portal is separate from the main staff authentication system.

## Authentication

Authentication shall use:

```text
AMKA
 +
OTP
 ↓
Temporary authenticated session
```

The OTP shall be valid for a limited period and shall not create a permanent patient account.

## Patient capabilities

### FR-PORTAL-001

The system shall allow a patient to request access to the Patient Portal using their AMKA.

### FR-PORTAL-002

The system shall verify the patient's identity using a One-Time Password.

### FR-PORTAL-003

The system shall allow an authenticated patient to view upcoming appointments.

### FR-PORTAL-004

The system shall allow an authenticated patient to cancel an eligible appointment.

### FR-PORTAL-005

The system shall allow an authenticated patient to request or perform appointment rescheduling where permitted.

### FR-PORTAL-006

The Patient Portal shall expose only information required for patient-facing functionality.

Clinical records shall not automatically be exposed through the Patient Portal.

---

# 7. Functional Requirements

## 7.1 Authentication

### FR-AUTH-001

The system shall allow authorized staff users to authenticate securely.

### FR-AUTH-002

The system shall associate authenticated staff with one or more roles.

### FR-AUTH-003

The system shall enforce permissions based on user roles.

### FR-AUTH-004

The system shall prevent users from accessing data belonging to clinics for which they are not authorized.

### FR-AUTH-005

The system shall support secure session or token expiration.

---

# 8. Clinic Management

### FR-CLINIC-001

The system shall represent each medical practice as an independent Clinic entity.

### FR-CLINIC-002

The system shall associate staff members with a clinic.

### FR-CLINIC-003

The system shall associate clinic-owned operational data with the appropriate clinic.

### FR-CLINIC-004

Authorized users shall be able to manage basic clinic information.

---

# 9. Staff and Role Management

### FR-USER-001

The system shall allow authorized users to create staff accounts.

### FR-USER-002

Each staff account shall contain authentication and account status information.

### FR-USER-003

The system shall support at least the following roles:

* OWNER
* DOCTOR
* SECRETARY

### FR-USER-004

The authorization model shall support a user acting both as Owner and Doctor.

### FR-USER-005

Doctor-specific information shall be stored separately from general authentication information where appropriate.

---

# 10. Patient Management

### FR-PAT-001

Authorized staff shall be able to register a patient.

### FR-PAT-002

Authorized staff shall be able to update patient demographic and contact information.

### FR-PAT-003

The system shall maintain a unique internal identifier for each patient.

### FR-PAT-004

The system shall support AMKA as a patient identification attribute.

### FR-PAT-005

Authorized users shall be able to search for patients.

### FR-PAT-006

Authorized users shall be able to access a patient's appointment history.

### FR-PAT-007

Clinical users shall be able to access the patient's medical history according to their permissions.

---

# 11. Appointment Management

Appointment management is a core component of the system.

### FR-APPT-001

Authorized staff shall be able to create an appointment.

### FR-APPT-002

An appointment shall be associated with a patient.

### FR-APPT-003

An appointment shall be associated with a doctor.

### FR-APPT-004

An appointment shall contain a start time and expected duration.

### FR-APPT-005

The system shall allow appointments to be rescheduled.

### FR-APPT-006

The system shall allow appointments to be cancelled.

### FR-APPT-007

The system shall record the status of an appointment.

Possible statuses may include:

```text
SCHEDULED
CONFIRMED
COMPLETED
CANCELLED
NO_SHOW
```

### FR-APPT-008

The system shall detect scheduling conflicts for the same doctor.

### FR-APPT-009

The system shall prevent invalid overlapping appointments unless an authorized workflow explicitly permits them.

### FR-APPT-010

Authorized users shall be able to view appointments by day, week and other appropriate date ranges.

### FR-APPT-011

The system shall maintain historical appointment information required for analytics and intelligent features.

---

# 12. Medical Records

### FR-MED-001

The system shall allow authorized doctors to create medical records associated with a patient.

### FR-MED-002

Medical records shall contain appropriate timestamps.

### FR-MED-003

Medical records shall identify the doctor responsible for the record.

### FR-MED-004

Doctors shall be able to view relevant historical medical records.

### FR-MED-005

Access to medical records shall be restricted according to authorization rules.

### FR-MED-006

Medical records shall remain logically separated between clinics.

---

# 13. Prescriptions

Prescription functionality may be included as a secondary clinical module.

### FR-PRES-001

Authorized doctors shall be able to record prescription information associated with a patient.

### FR-PRES-002

A prescription shall identify the responsible doctor.

### FR-PRES-003

The system shall maintain prescription history where the module is enabled.

The initial version does not aim to replace official electronic prescription systems.

---

# 14. Payments

The Payment module is an internal record-keeping and analytics feature.

It is **not an invoicing, accounting or receipt-generation system**.

### FR-PAY-001

Authorized users shall be able to record a payment.

### FR-PAY-002

A payment shall include an amount.

### FR-PAY-003

A payment shall include a payment method.

Possible payment methods may include:

```text
CASH
CARD
BANK_TRANSFER
OTHER
```

### FR-PAY-004

A payment shall contain the date and time of the transaction.

### FR-PAY-005

A payment shall be associated with a patient.

### FR-PAY-006

A payment may optionally be associated with an appointment.

### FR-PAY-007

Authorized users shall be able to view payment history.

### FR-PAY-008

Payment information shall be available for statistical calculations.

The system shall not generate tax documents, receipts or invoices in version 1.0.

---

# 15. Dashboard and Analytics

The application shall provide operational information to authorized users.

Possible statistics include:

* Appointments per day/week/month.
* Completed appointments.
* Cancelled appointments.
* No-show rate.
* Patient activity.
* Revenue by period.
* Revenue by doctor.
* Revenue by service, where service information exists.
* Distribution by payment method.

### FR-STAT-001

The system shall provide basic appointment statistics.

### FR-STAT-002

The system shall provide basic payment statistics.

### FR-STAT-003

Financial information shall only be visible to authorized roles.

### FR-STAT-004

Statistical calculations shall derive from operational data stored by the system.

---

# 16. Notifications and Core Automation

Core automation refers to deterministic functionality and shall be separated conceptually from intelligent features.

## Appointment Conflict Detection

The system shall automatically detect appointment conflicts.

## Appointment Reminders

### FR-NOT-001

The system shall support reminders for upcoming appointments.

### FR-NOT-002

Reminder scheduling shall be configurable where appropriate.

## Follow-Up Reminders

### FR-NOT-003

The system shall support follow-up reminders where a doctor or workflow indicates that future contact is required.

## Internal Notifications

### FR-NOT-004

The system shall be able to notify appropriate staff about relevant system events.

---

# 17. Intelligent Features

Intelligent features shall be implemented separately from standard automation.

Their purpose is to provide recommendations or predictions rather than replace medical decision-making.

## 17.1 No-Show Risk Estimation

The system may analyze historical appointment information such as:

* Previous appointments.
* Previous cancellations.
* Previous no-shows.
* Appointment day and time.
* Relevant historical patterns.

The result may be represented as a risk score or risk category.

Example:

```text
Appointment History
        ↓
Feature extraction
        ↓
Risk estimation
        ↓
LOW / MEDIUM / HIGH
        ↓
Possible additional reminder
```

### IFR-NS-001

The system shall be capable of calculating or estimating a no-show risk for eligible appointments.

### IFR-NS-002

The factors contributing to the estimation shall be documented.

### IFR-NS-003

No-show estimation shall not automatically cancel or reject an appointment.

---

## 17.2 Smart Availability Suggestions

The system may recommend appointment slots based on factors including:

* Doctor availability.
* Existing appointments.
* Appointment duration.
* Scheduling constraints.
* Historical information where useful.

### IFR-SA-001

The system shall be capable of identifying valid available appointment slots.

### IFR-SA-002

The system may rank available slots according to predefined or learned criteria.

### IFR-SA-003

Final appointment selection shall remain under user control.

---

## 17.3 Patient Alerts

The system may identify predefined conditions or patterns that require staff attention.

### IFR-PA-001

The system may generate alerts based on explicitly defined patient-related rules or algorithms.

### IFR-PA-002

The reason for an alert shall be available to the authorized user.

### IFR-PA-003

Patient alerts shall assist staff and shall not independently make medical decisions.

---

# 18. Domain Model

The initial conceptual domain model consists of:

```text
Clinic
│
├── User
│   └── Role
│
├── DoctorProfile
│
├── Patient
│
├── Appointment
│
├── MedicalRecord
│
├── Prescription
│
├── Payment
│
└── Notification
```

Major relationships include:

```text
Clinic
  │
  ├── Users
  ├── Patients
  ├── Appointments
  ├── MedicalRecords
  └── Payments


User
  │
  └── DoctorProfile (when applicable)


Patient
  │
  ├── Appointments
  ├── MedicalRecords
  ├── Prescriptions
  └── Payments


Doctor
  │
  ├── Appointments
  ├── MedicalRecords
  └── Prescriptions


Appointment
  │
  ├── Patient
  ├── Doctor
  └── Payment (optional)
```

The exact relational database schema shall be defined separately in the Database Design specification.

---

# 19. Authentication and Authorization Architecture

Two independent authentication flows shall exist.

## Staff Authentication

```text
Credentials
    ↓
Authentication API
    ↓
User verification
    ↓
Session / JWT
    ↓
Role + Clinic authorization
```

## Patient Authentication

```text
AMKA
 ↓
OTP request
 ↓
OTP verification
 ↓
Temporary Patient Portal session
 ↓
Restricted appointment functionality
```

Patient Portal authorization must never be treated as equivalent to staff authorization.

---

# 20. System Architecture

The application shall follow a layered architecture.

```text
┌───────────────────────────────┐
│       Presentation Layer      │
│      React / TypeScript       │
└───────────────┬───────────────┘
                │ HTTP / REST
                ▼
┌───────────────────────────────┐
│           API Layer           │
│            FastAPI            │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│        Service Layer          │
│      Business Logic           │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│      Data Access Layer        │
│          SQLAlchemy           │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│          PostgreSQL           │
└───────────────────────────────┘
```

Business logic should not be unnecessarily placed inside API route handlers.

API routes should primarily handle:

* Request parsing.
* Validation.
* Authorization.
* Service invocation.
* HTTP responses.

The Service Layer should contain the main application business rules.

---

# 21. API Architecture

The backend shall expose a REST API.

Potential resource groups include:

```text
/api/auth
/api/clinics
/api/users
/api/doctors
/api/patients
/api/appointments
/api/medical-records
/api/prescriptions
/api/payments
/api/notifications
/api/statistics
/api/portal
```

The exact endpoints and request/response schemas shall be defined in a separate API specification.

The API shall:

* Use appropriate HTTP methods.
* Return appropriate HTTP status codes.
* Validate input.
* Enforce authorization.
* Maintain tenant isolation.
* Avoid exposing unnecessary sensitive information.

---

# 22. Frontend Architecture

The frontend shall be implemented using React and TypeScript.

The application shall conceptually contain two interfaces.

## Staff Application

Potential areas include:

```text
Login

Dashboard

Patients
├── Patient List
├── Patient Details
└── Medical History

Appointments
├── Calendar
├── Create Appointment
├── Edit Appointment
└── Appointment Details

Payments

Statistics

Notifications

Settings
```

## Patient Portal

```text
Patient Verification
       ↓
AMKA + OTP
       ↓
Appointments
├── View
├── Cancel
└── Reschedule
```

The Patient Portal shall remain logically separated from the main staff interface.

---

# 23. Non-Functional Requirements

## NFR-001 — Security

Sensitive information shall be accessible only to authorized users.

## NFR-002 — Privacy

The system shall minimize unnecessary exposure of patient information.

## NFR-003 — Tenant Isolation

Clinic data shall remain logically isolated.

## NFR-004 — Maintainability

The codebase shall follow a modular architecture with clear responsibilities.

## NFR-005 — Extensibility

New modules should be introducible without major architectural redesign.

## NFR-006 — Usability

The interface shall be suitable for users without advanced technical knowledge.

## NFR-007 — Performance

Normal operations such as patient search and appointment retrieval should provide responsive interaction under the expected workload of small and medium-sized practices.

## NFR-008 — Data Integrity

Relationships and constraints shall prevent inconsistent data where reasonably possible.

## NFR-009 — Auditability

Important operations should retain sufficient information to determine when and by whom relevant changes were made.

## NFR-010 — Reliability

Failures in secondary functionality such as notifications should not unnecessarily compromise core patient and appointment functionality.

---

# 24. Security Requirements

Security shall be considered throughout the system design.

The system shall include:

* Secure password hashing.
* Secure authentication tokens or sessions.
* OTP expiration.
* Protection against OTP brute-force attempts.
* Rate limiting where appropriate.
* Role-based authorization.
* Tenant-level authorization.
* Input validation.
* Protection of sensitive configuration through environment variables.
* Appropriate database constraints.
* Secure API error handling.
* Restricted exposure of medical information.
* Appropriate logging without leaking sensitive information.

AMKA and other sensitive patient information must not be unnecessarily exposed through API responses, logs or client-side storage.

Security decisions shall be reviewed separately before production deployment.

---

# 25. Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy 2.x
* Alembic
* Pydantic

## Database

* PostgreSQL

## Frontend

* React
* TypeScript
* Vite

## Infrastructure

* Docker
* Docker Compose

## Version Control

* Git
* GitHub

## Development Tools

The development workflow may use AI-assisted engineering tools including:

* Cursor
* Codex
* ChatGPT
* Claude Code

AI-generated code remains subject to human review, testing and the requirements defined in this specification.

---

# 26. MVP Scope

Not every planned feature has equal priority.

## Core MVP

The initial working system should prioritize:

1. Clinic / tenant foundation.
2. Staff authentication.
3. Role-based authorization.
4. Patient management.
5. Doctor management.
6. Appointment management.
7. Scheduling conflict detection.
8. Medical records.
9. Basic dashboard.
10. Patient Portal with AMKA + OTP.
11. Appointment reminders.

These features constitute the core operational system.

---

## Secondary Features

After the core system is stable:

* Payment recording.
* Financial statistics.
* Prescriptions.
* Advanced notifications.
* Follow-up workflows.
* Extended dashboard analytics.

---

## Intelligent Features

After sufficient operational functionality and data structures exist:

* No-show risk estimation.
* Smart appointment availability.
* Patient alerts.
* Intelligent reminder optimization.

This ordering is intentional because intelligent functionality depends on reliable underlying data and business logic.

---

# 27. Out of Scope for Version 1.0

The following functionality is not required for the initial version:

* Tax receipt generation.
* Invoice generation.
* Full accounting functionality.
* Integration with official electronic prescription infrastructure.
* Hospital-level EHR functionality.
* Insurance claim processing.
* Automated SaaS subscription billing.
* Autonomous medical diagnosis.
* Autonomous medical decision-making.

These may be considered as future extensions where appropriate.

---

# 28. Development Principles

Development shall follow the following principles.

### Specification before implementation

Major functionality should be defined before code is written.

### Small development tasks

Features should be divided into independently reviewable tasks.

### Human review of AI output

AI-generated modifications shall not be accepted blindly.

### Testing

New functionality should include appropriate tests.

### Database migrations

Database schema modifications shall use Alembic migrations.

### Separation of concerns

Presentation, API, business logic and persistence concerns should remain appropriately separated.

### Minimal unrelated modifications

A development task should not unnecessarily modify unrelated parts of the codebase.

### Documentation

Important architectural and technical decisions shall be documented.

---

# 29. Development Workflow

The recommended workflow for each feature is:

```text
Requirement
    ↓
Design / Analysis
    ↓
Implementation Plan
    ↓
Feature Branch
    ↓
Implementation
    ↓
Automated Tests
    ↓
Code Review
    ↓
Manual Verification
    ↓
Documentation
    ↓
Merge
```

AI coding agents may participate in analysis, implementation, testing and review but shall operate according to the project specification and repository instructions.

---

# 30. Planned Supporting Documentation

The System Specification shall act as the central reference document.

Additional documentation should be maintained separately:

```text
docs/
│
├── system-specification.md
│
├── requirements/
│   ├── functional-requirements.md
│   └── non-functional-requirements.md
│
├── architecture/
│   ├── system-architecture.md
│   ├── database-design.md
│   └── architecture-decisions.md
│
├── api/
│   └── api-specification.md
│
├── intelligent-features/
│   └── intelligent-features-design.md
│
└── development/
    ├── roadmap.md
    └── development-log.md
```

---

# 31. Future Extensions

Potential future extensions include:

* SaaS subscription management.
* Multiple clinic locations.
* More advanced staff permission management.
* Integration with external calendars.
* SMS/email providers.
* Advanced reporting.
* Data export.
* Advanced scheduling optimization.
* Machine-learning-based no-show prediction.
* Mobile application.
* Integration with external healthcare systems.
* Advanced audit logging.
* Backup and recovery mechanisms.

These extensions should not unnecessarily complicate the initial MVP architecture.

---

# 32. Specification Status

This document represents **System Specification v1.0**.

It defines the agreed initial scope and architecture of the application and should serve as the primary technical reference during development.

Changes to important architectural decisions, authentication models, domain relationships, tenant isolation or core requirements should be reflected in future versions of this specification.

The next design documents to be produced from this specification are:

**1. Database Design v1.0**
**2. Authorization / Role Matrix v1.0**
**3. API Specification v1.0**
**4. Intelligent Features Design v1.0**
**5. Development Roadmap v1.0**
**6. AGENTS.md**

Once these documents are established, implementation tasks can be mapped directly to requirement identifiers such as `FR-APPT-008`, `FR-PAT-001` or `IFR-NS-001`.
