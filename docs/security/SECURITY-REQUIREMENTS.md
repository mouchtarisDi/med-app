# Απαιτήσεις Ασφάλειας — med-app

## 1. Στοιχεία εγγράφου

| Πεδίο | Τιμή |
|---|---|
| Εργασία | SECURITY-00A |
| Έκδοση | 1.0 |
| Ημερομηνία | 2026-10-30 |
| Κατάσταση | Αρχική τεκμηριωμένη βάση απαιτήσεων· δεν αποτελεί έγκριση παραγωγής |
| Branch αναφοράς | `feature/clinic-authorization` |
| HEAD επιθεώρησης | `985d7567dda50f8967911c0c18a1785433a80a4c` |
| Κύρια προδιαγραφή | [System Specification v1.0](../system-specification.md) |
| Μέθοδος | Προηγούμενη επιθεώρηση μόνο ανάγνωσης και στοχευμένη επανεπιθεώρηση πηγαίου κώδικα και tests |
| Εξουσιοδοτημένη χρήση | Ανάπτυξη και ακαδημαϊκή επίδειξη αποκλειστικά με συνθετικά δεδομένα |

Το έγγραφο εξειδικεύει τις ενότητες 5–6, 19, 23–24 της προδιαγραφής και τα `FR-AUTH-001`–`FR-AUTH-005`, `FR-MED-005`–`FR-MED-006`, `FR-PORTAL-006`, `NFR-001`–`NFR-003`, `NFR-008`–`NFR-010`. Δεν αλλάζει μοντέλα, endpoints ή αρχιτεκτονική. Οι αποφάσεις του project owner που καταγράφονται παρακάτω αποτελούν τη βάση της πολιτικής.

**Δεν επιτρέπονται πραγματικά δεδομένα ασθενών ή δημόσια παραγωγική χρήση στο παρόν στάδιο. Η συμμόρφωση με τον GDPR δεν έχει τεκμηριωθεί.** Η αρχιτεκτονική πρέπει να υποστηρίζει μελλοντική χρήση από ιατρεία, αλλά αυτή προϋποθέτει ανεξάρτητο production-readiness gate και ρητή νέα έγκριση.

## 2. Πεδίο, τεκμήρια και συμβάσεις

### 2.1 Βάση τεκμηρίωσης

Οι διαδρομές είναι σχετικές προς τη ρίζα του repository. Οι σύνδεσμοι στον κατάλογο τεκμηρίων οδηγούν στα αρχεία. Η παρούσα κατάσταση αφορά το παραπάνω HEAD, όχι άγνωστη υποδομή ή μελλοντική υλοποίηση.

| Κωδικός | Πηγή |
|---|---|
| E01 | [Authentication API](../../backend/app/api/auth.py), [User schemas](../../backend/app/schemas/user.py), [User model](../../backend/app/db/models/user.py) |
| E02 | [Security utilities](../../backend/app/core/security.py), [Settings](../../backend/app/core/config.py) |
| E03 | [Authentication/clinic dependencies](../../backend/app/api/deps.py), [Permission policy](../../backend/app/core/permissions.py) |
| E04 | [Clinic](../../backend/app/db/models/clinic.py), [ClinicMembership](../../backend/app/db/models/clinic_membership.py), [MembershipRole](../../backend/app/db/models/membership_role.py) |
| E05 | [Application routes](../../backend/app/main.py), [Database session](../../backend/app/db/session.py) |
| E06 | [AuthProvider](../../frontend/src/auth/AuthProvider.tsx), [ProtectedRoute](../../frontend/src/auth/ProtectedRoute.tsx), [App](../../frontend/src/App.tsx) |
| E07 | [API client](../../frontend/src/api/client.ts), [Auth API client](../../frontend/src/api/auth.ts), [LoginPage](../../frontend/src/pages/LoginPage.tsx) |
| E08 | [Compose](../../docker-compose.yml), [Backend Dockerfile](../../backend/Dockerfile), [Frontend Dockerfile](../../frontend/Dockerfile), [Vite configuration](../../frontend/vite.config.ts) |
| E09 | [.env.example](../../.env.example), [.gitignore](../../.gitignore), [Alembic environment](../../backend/alembic/env.py), [Alembic configuration](../../backend/alembic.ini) |
| E10 | [User migration](../../backend/alembic/versions/71eda1fd3061_create_users_table.py), [Clinic/membership migration](../../backend/alembic/versions/a807f733a8e3_create_clinic_membership_tables.py) |
| E11 | [Backend dependencies](../../backend/requirements.txt), [Test dependencies](../../backend/requirements-test.txt), [Frontend manifest](../../frontend/package.json) |
| E12 | [Test bootstrap](../../backend/tests/conftest.py), [Test Compose](../../docker-compose.test.yml), [Frontend test runner](../../frontend/tests/run-api-tests.mjs) |

Οι αναφορές T01–T11 ορίζονται στην ενότητα 10. Περιγράφουν υπάρχοντα test assertions που επιθεωρήθηκαν, **όχι tests που εκτελέστηκαν στο SECURITY-00A**. Δεν εκτελέστηκαν application tests ή migrations κατά τη σύνταξη. Το backend database fixture εκτελεί Alembic upgrade όταν χρησιμοποιείται· η ύπαρξή του δεν αποτελεί απόδειξη επιτυχούς migration ή test run.

Δεν επιθεωρήθηκαν πραγματικές τιμές μυστικών, ζωντανή εγκατάσταση, Git history για secrets ή εγκατεστημένες εξαρτήσεις για vulnerabilities. Το `README.md` είναι κενό και δεν βρέθηκαν ξεχωριστά security/deployment/backup runbooks ή CI security gates στην προηγούμενη επιθεώρηση.

### 2.2 Καταστάσεις και προτεραιότητες

| Κατάσταση | Σημασία |
|---|---|
| Υλοποιημένο (Implemented) | Υπάρχει κώδικας για το δηλωμένο, περιορισμένο πεδίο. Δεν σημαίνει πιστοποίηση ή επιτυχή πρόσφατη εκτέλεση tests. |
| Μερικό (Partial) | Υπάρχει τμήμα του ελέγχου, αλλά δεν καλύπτονται όλα τα κριτήρια. |
| Προγραμματισμένο (Planned) | Απαίτηση της προδιαγραφής ή εγκεκριμένος σχεδιασμός, χωρίς τεκμηριωμένη υλοποίηση. |
| Άγνωστο (Unknown) | Δεν υπάρχουν επαρκή repository evidence για υλοποίηση ή επιχειρησιακή εφαρμογή. |

Οι ενδείξεις «foundation» και «τρέχουσα ροή» περιορίζουν ρητά το εύρος μιας κατάστασης. Η απουσία evidence δεν αποδεικνύει απουσία ελέγχου σε εξωτερική υποδομή.

- **P0:** υποχρεωτική επίλυση πριν από πραγματικά δεδομένα ή δημόσια παραγωγική έκθεση.
- **P1:** υποχρεωτική ολοκλήρωση πριν από διάθεση της σχετικής λειτουργίας· αν αυτή περιλαμβάνεται στην παραγωγή, αποτελεί επίσης blocker.
- **P2:** περαιτέρω ενίσχυση μετά την κάλυψη των βασικών gates.

Το «πρέπει» δηλώνει απαίτηση στόχου. Τα κριτήρια είναι ελέγξιμα, αλλά δεν θεωρούνται ήδη ικανοποιημένα. Όπου απαιτείται αριθμητικό όριο, εφαρμόζεται μόνο τεκμηριωμένη, εγκεκριμένη τιμή. Μη καθορισμένο όριο αφήνει το αντίστοιχο κριτήριο ανοικτό.

## 3. Περιβάλλον χρήσης και εγκεκριμένες αποφάσεις

1. Η ανάπτυξη και η επίδειξη χρησιμοποιούν αποκλειστικά συνθετικά δεδομένα. Αντιγραφή ή απλή ψευδωνυμοποίηση πραγματικών φακέλων δεν ικανοποιεί αυτόν τον περιορισμό.
2. Η μελλοντική λειτουργία για πραγματικά ιατρεία αποτελεί αρχιτεκτονικό στόχο, όχι τρέχουσα άδεια χρήσης.
3. Ο OWNER έχει όλες τις permissions της δικής του Clinic, συμπεριλαμβανομένων `medical_records.read` και `medical_records.write`, ακόμη και χωρίς DOCTOR. Ποτέ δεν παρακάμπτει clinic boundaries.
4. Πολλαπλοί ρόλοι συνδυάζονται προσθετικά μόνο εντός της ίδιας clinic membership. Ρόλος σε άλλη Clinic δεν προσθέτει δικαιώματα στο τρέχον context.
5. Η μελλοντική ένταξη προσωπικού πρέπει να ευνοεί αρχικό OWNER bootstrap και invitations για DOCTOR/SECRETARY. Αυτός ο σχεδιασμός είναι **Planned**. Το σημερινό δημόσιο `/auth/register` δεν αποτελεί υλοποίησή του και δεν αποδίδει clinic membership.
6. Αριθμητικές πολιτικές και νομικά συμπεράσματα δεν τεκμαίρονται από αυτό το έγγραφο.

## 4. Actors, assets και ταξινόμηση δεδομένων

| Actor | Όριο εμπιστοσύνης / επιτρεπόμενος σκοπός |
|---|---|
| OWNER | Πλήρης πρόσβαση μόνο στη δική του Clinic σύμφωνα με το RBAC matrix. |
| DOCTOR | Κλινικές και λειτουργικές ενέργειες που αποδίδει το matrix· πρόσθετοι περιορισμοί ανά ασθενή/ανάθεση παραμένουν προς απόφαση. |
| SECRETARY | Διοικητικές λειτουργίες χωρίς clinical permissions, εκτός αν ο ίδιος χρήστης έχει πρόσθετο κατάλληλο ρόλο στην ίδια Clinic. |
| Patient | Ξεχωριστή, μελλοντική AMKA + OTP ταυτότητα· μόνο επιτρεπόμενες ενέργειες ραντεβού. Δεν είναι staff User. |
| Μη authenticated επισκέπτης / επιτιθέμενος | Καμία εμπιστοσύνη· πρόσβαση μόνο στα ρητά public endpoints. |
| Διαχειριστής υποδομής / πάροχος | Ξεχωριστή επιχειρησιακή πρόσβαση που χρειάζεται έλεγχο, καταγραφή και καθορισμό ευθυνών. Δεν αποτελεί αυτόματο application role. |

| Κατηγορία | Assets / δεδομένα | Χειρισμός στόχου |
|---|---|---|
| Μυστικά ασφάλειας | Passwords, hashes, JWTs, OTPs, signing keys, DB/provider credentials | Ελάχιστη πρόσβαση· όχι σε responses, URLs, logs ή repository, εκτός του απαραίτητου token response. |
| Ιδιαίτερα ευαίσθητα δεδομένα στόχου | Medical records, ιστορικό, συνταγές, AMKA και συνδέσεις με περίθαλψη | Αυστηρή εξουσιοδότηση, tenant scope και ελαχιστοποίηση. Σήμερα επιτρέπονται μόνο συνθετικές αναπαραστάσεις. |
| Εμπιστευτικά λειτουργικά δεδομένα | Στοιχεία ασθενών/προσωπικού, ραντεβού, πληρωμές, memberships, analytics | Περιορισμός ανά Clinic και σκοπό· τα metadata μπορεί να αποκαλύπτουν πληροφορίες υγείας. |
| Δεδομένα ελέγχου και υποδομής | Audit events, logs, backups, exports, configuration | Περιορισμένη πρόσβαση και retention· κληρονομούν την ευαισθησία του περιεχομένου τους. |
| Δημόσια στοιχεία | Εγκεκριμένη γενική τεκμηρίωση και μη ευαίσθητη ένδειξη λειτουργίας | Καμία αποκάλυψη δεδομένων tenant ή λεπτομερειών μυστικών/υποδομής. |

Τα συνθετικά datasets δεν αίρουν την ανάγκη προστασίας πραγματικών developer credentials και υποδομής. Patient, Appointment, MedicalRecord και Payment λειτουργίες δεν τεκμηριώνονται ως υλοποιημένες στο baseline.

## 5. Στόχοι ασφάλειας και trust boundaries

Στόχοι είναι η εμπιστευτικότητα, η ακεραιότητα, η διαθεσιμότητα, η λογοδοσία, η ελαχιστοποίηση δεδομένων και η ασφαλής αστοχία. Η αποτυχία εξουσιοδότησης δεν πρέπει να μετατρέπεται σε επιτρεπόμενη πρόσβαση.

| Boundary | Απαιτούμενη αντιμετώπιση |
|---|---|
| Browser → API | Κάθε input και client-side role/context θεωρείται μη έμπιστο. Backend authentication/authorization είναι υποχρεωτικά. |
| JWT → database identity | Το υπογεγραμμένο `sub` ταυτοποιεί χρήστη· δεν αποδεικνύει τρέχουσα ενεργοποίηση, membership ή permissions. |
| User → Clinic | Το `clinic_id` ελέγχεται με membership του authenticated χρήστη. |
| Clinic → resource | Κάθε object query, συσχέτιση, aggregate και export χρειάζεται tenant scope. Το membership check μόνο του δεν αρκεί. |
| Staff → Patient Portal | Ανεξάρτητες ταυτότητες, sessions και επιτρεπόμενες λειτουργίες. |
| API → DB / providers / backups | Διακριτά credentials, least privilege, ασφαλής μεταφορά και περιορισμός αντιγράφων. |
| Development → production | Ρητή αλλαγή περιβάλλοντος, configuration και έγκριση μετά το production gate. |

## 6. Κατάλογος απαιτήσεων

### SEC-001 — Προμήθεια και δημιουργία staff accounts

- **Περιγραφή:** Η δημιουργία staff accounts πρέπει να ακολουθεί εγκεκριμένο OWNER bootstrap και invitation workflow, χωρίς αυτόματη ανάθεση μη εξουσιοδοτημένων clinic roles.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό· bootstrap/invitations Προγραμματισμένα.
- **Κριτήρια αποδοχής:** Κάθε account-creation path έχει καθορισμένο actor και clinic scope. Μη εξουσιοδοτημένα invitations/role assignments απορρίπτονται. Η δημόσια registration πολιτική έχει αντικατασταθεί ή ρητά περιοριστεί πριν από παραγωγή. Invitation lifecycle ελέγχεται με tests.
- **Evidence / κενό:** E01: δημόσιο `/auth/register`, χωρίς membership assignment. Δεν υπάρχει bootstrap/invitation implementation ή σχετική test evidence.

### SEC-002 — Ασφαλής αποθήκευση και πολιτική passwords

- **Περιγραφή:** Τα passwords πρέπει να αποθηκεύονται μόνο ως εγκεκριμένα adaptive hashes και να έχουν τεκμηριωμένα όρια και χειρισμό κωδικοποίησης.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Πραγματικά hash/verify tests επιβεβαιώνουν σωστό και λανθασμένο password και μη αποθήκευση plaintext. Εγκεκριμένα όρια μήκους, UTF-8 byte boundaries και hash work factor εφαρμόζονται χωρίς σιωπηρή αλλοίωση ή ανεξέλεγκτα errors.
- **Evidence / κενό:** E02: Passlib bcrypt. E01: password ως απλό `str`, χωρίς bounds. T01 χρησιμοποιεί mocked verification στο login· δεν αποδεικνύει πραγματικό hashing.

### SEC-003 — Κατάσταση και απενεργοποίηση χρήστη

- **Περιγραφή:** Μόνο ενεργοί χρήστες πρέπει να λαμβάνουν tokens και να προσπελαύνουν protected APIs.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Inactive χρήστης δεν λαμβάνει νέο token. Υπάρχον token απορρίπτεται μετά από deactivation. Ανύπαρκτος χρήστης και μη ενεργή/μη καθορισμένη κατάσταση δεν επιτρέπουν πρόσβαση.
- **Evidence / κενό:** E03 και T02/T03 ελέγχουν τρέχοντα χρήστη και active status. E01: login δεν ελέγχει activation και registration δημιουργεί χρήστη με active default. Activation workflow απουσιάζει.

### SEC-004 — Ασφαλείς αποτυχίες authentication

- **Περιγραφή:** Τα authentication errors δεν πρέπει να διευκολύνουν enumeration ή να αποκαλύπτουν credentials.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Άγνωστος λογαριασμός και λάθος password επιστρέφουν ίδιο public status/body. Ελέγχονται enumeration μέσω registration και χρονικές αποκλίσεις με εγκεκριμένη μέθοδο/ανοχή. Μη έγκυρα credentials δεν αποκαλύπτονται σε responses/logs.
- **Evidence / κενό:** E01: κοινό login error, αλλά διαφορετικό duplicate-email registration error και short-circuit πριν το hashing για άγνωστο χρήστη. Δεν υπάρχουν πλήρη failed-login/timing tests.

### SEC-005 — Recovery και αλλαγή credentials

- **Περιγραφή:** Η ανάκτηση πρόσβασης και οι αλλαγές password πρέπει να έχουν ρητή ασφαλή πολιτική.
- **Προτεραιότητα / κατάσταση:** P1 · Άγνωστο.
- **Κριτήρια αποδοχής:** Εφόσον προσφερθεί recovery, τα recovery tokens είναι περιορισμένης διάρκειας και single-use· expired/replayed tokens απορρίπτονται. Password changes και recovery εφαρμόζουν την εγκεκριμένη session-invalidation πολιτική. Αν η λειτουργία αποκλειστεί, τεκμηριώνεται ασφαλής διοικητική διαδικασία.
- **Evidence / κενό:** Δεν βρέθηκαν recovery/password-change endpoints ή tests στο E01/E05.

### SEC-006 — JWT signing και validation

- **Περιγραφή:** Τα access tokens πρέπει να έχουν υπογραφή, λήξη, έγκυρη ταυτότητα και σαφή σκοπό χρήσης.
- **Προτεραιότητα / κατάσταση:** P1 · Μερικό συνολικά· υλοποιημένος βασικός validator.
- **Κριτήρια αποδοχής:** Απορρίπτονται invalid signatures, disallowed algorithms, expired tokens και missing/invalid claims. Τεκμηριώνεται token-purpose contract και απόφαση για issuer/audience. Υπάρχουν αρνητικά tests για κάθε εγκεκριμένο κανόνα.
- **Evidence / κενό:** E02, T01: απαιτούνται `sub` και `exp`, ελέγχεται positive PostgreSQL Integer identity και configured algorithm. Δεν τεκμηριώνονται issuer/audience ή ξεχωριστός portal token validator.

### SEC-007 — Session lifecycle και logout

- **Περιγραφή:** Η διάρκεια και η ανάκληση sessions πρέπει να αντιστοιχούν σε εγκεκριμένη πολιτική.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Καθορίζονται absolute/idle lifetime, concurrent sessions, logout και password-change invalidation. Expiration και replay tests αποδεικνύουν τη δηλωμένη συμπεριφορά. Κάθε επιτρεπόμενο παράθυρο replay καταγράφεται ως αποδεκτός κίνδυνος πριν από παραγωγή.
- **Evidence / κενό:** E02: configurable expiry με υπάρχον default 30 λεπτών, όχι νέα εγκεκριμένη production τιμή. E06/T08: logout καθαρίζει μόνο client state. Δεν υπάρχει server-side revocation ή refresh workflow.

### SEC-008 — Χειρισμός tokens στον browser

- **Περιγραφή:** Tokens/passwords δεν πρέπει να αποθηκεύονται μόνιμα στον browser ή να εμφανίζονται σε UI/URLs.
- **Προτεραιότητα / κατάσταση:** P1 · Υλοποιημένο στην τρέχουσα περιορισμένη ροή.
- **Κριτήρια αποδοχής:** Δεν γίνονται writes σε persistent browser storage για credentials/tokens. Logout/remount αφαιρούν authentication state, late responses δεν το επαναφέρουν και DOM/URLs δεν εκθέτουν tokens/passwords.
- **Evidence / κενό:** E06/E07, T08–T11: memory-only state, ασφαλής διαχείριση pending login, clearing password. Δεν αποτελεί προστασία από XSS· η επέκταση σε νέα API flows απαιτεί νέα verification.

### SEC-009 — Προστασία endpoints και current user

- **Περιγραφή:** Κάθε endpoint πρέπει να ταξινομείται ως public ή protected· τα protected endpoints ελέγχουν server-side την τρέχουσα ταυτότητα.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Υπάρχει εγκεκριμένο public allowlist, συμπεριλαμβανομένων docs/health endpoints. Όλα τα υπόλοιπα απορρίπτουν missing/invalid/expired tokens και ανύπαρκτους/inactive χρήστες. UI guards δεν υποκαθιστούν backend checks.
- **Evidence / κενό:** E01/E03/E05 και T02/T03: `/auth/me` προστατεύεται. `/auth/register`, `/auth/login`, `/` και `/health/db` είναι public· FastAPI docs δεν περιορίζονται με ρητή ρύθμιση. Δεν υπάρχει ολοκληρωμένο endpoint classification.

### SEC-010 — Επαλήθευση Clinic context

- **Περιγραφή:** Το clinic context πρέπει να προκύπτει από membership του authenticated χρήστη στην αιτούμενη Clinic.
- **Προτεραιότητα / κατάσταση:** P1 · Υλοποιημένο ως foundation.
- **Κριτήρια αποδοχής:** Invalid clinic IDs απορρίπτονται. Ανύπαρκτη και μη προσβάσιμη Clinic δίνουν ισοδύναμο public response. Membership changes επανελέγχονται με ίδιο JWT. Το `is_superuser` δεν παρακάμπτει membership.
- **Evidence / κενό:** E03/E04, T04. Έλεγχος μέσω test-only routes· δεν υπάρχουν production clinic resource routes στο baseline.

### SEC-011 — Clinic-scoped additive RBAC

- **Περιγραφή:** Εφαρμόζεται αποκλειστικά το εγκεκριμένο matrix της ενότητας 7, με union permissions μόνο στην ίδια membership.
- **Προτεραιότητα / κατάσταση:** P0 · Υλοποιημένο ως foundation.
- **Κριτήρια αποδοχής:** Tests καλύπτουν το ακριβές matrix, multi-role unions, κενά roles, cross-clinic role leakage και έλλειψη superuser bypass. Role changes ισχύουν χωρίς νέο JWT. Κάθε νέα Permission επανεξετάζεται ως προς OWNER access.
- **Evidence / κενό:** E03 και T05/T06. Ο OWNER λαμβάνει όλο το `Permission` enum. Η εφαρμογή της πολιτικής σε μελλοντικά domain endpoints παραμένει υποχρεωτική.

### SEC-012 — Απομόνωση resources ανά tenant

- **Περιγραφή:** Κάθε clinic-owned resource και συσχέτιση πρέπει να περιορίζεται στη σωστή Clinic σε query και authorization επίπεδο.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό μόνο στο membership foundation· μη υλοποιημένο για Patient resources.
- **Κριτήρια αποδοχής:** Read/create/update/delete, lists, search, bulk operations, analytics και exports έχουν αρνητικά cross-clinic tests. Αντικατάσταση resource IDs και σύνδεση αντικειμένων άλλης Clinic απορρίπτονται. Τα tests περιλαμβάνουν OWNER και χρήστη με memberships σε περισσότερες Clinics.
- **Evidence / κενό:** E03/T04/T06 προστατεύουν membership context. Δεν υπάρχουν Patient resource models/routes ή resource-level isolation tests. Δεν τεκμαίρεται καθολική ORM απομόνωση ή database row-level security.

### SEC-013 — Περιορισμός clinical access

- **Περιγραφή:** Clinical data διατίθενται μόνο στους εγκεκριμένους clinic roles και στα απαραίτητα πεδία.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό σε επίπεδο permission policy.
- **Κριτήρια αποδοχής:** OWNER χωρίς DOCTOR επιτρέπεται εντός δικής του Clinic και απορρίπτεται εκτός αυτής. SECRETARY χωρίς πρόσθετο clinical role απορρίπτεται. Πραγματικά domain endpoints και response fields ελέγχονται με role/tenant tests.
- **Evidence / κενό:** E03/T05/T06 επιβεβαιώνουν policy foundations. Clinical endpoints/field-level tests απουσιάζουν. Η ευρεία OWNER πρόσβαση απαιτεί auditability και ενημέρωση της πολιτικής ιδιωτικότητας.

### SEC-014 — Διαχωρισμός Patient Portal identity

- **Περιγραφή:** Το μελλοντικό AMKA + OTP flow πρέπει να παραμένει ανεξάρτητο από staff authentication.
- **Προτεραιότητα / κατάσταση:** P1 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Patient sessions δεν εξουσιοδοτούν staff APIs. Token/session confusion και cross-patient requests απορρίπτονται. Οι patient sessions δεν δημιουργούν μόνιμα staff credentials.
- **Evidence / κενό:** Προδιαγραφή §§6, 19. Δεν υπάρχει Patient Portal implementation ή test evidence.

### SEC-015 — OTP lifecycle και προστασία επανάχρησης

- **Περιγραφή:** OTPs πρέπει να λήγουν, να εξαργυρώνονται ατομικά μία φορά και να αντιστέκονται σε brute force.
- **Προτεραιότητα / κατάσταση:** P1 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Εγκρίνονται entropy, validity, resend και attempt policies. Expired, replayed, λάθος και cross-patient codes απορρίπτονται, ακόμη και σε concurrent redemption. OTP values δεν καταγράφονται ή αποθηκεύονται σε ανακτήσιμη μορφή χωρίς εγκεκριμένη αιτιολόγηση.
- **Evidence / κενό:** Προδιαγραφή §§6, 24. Απουσιάζουν provider, destination verification, storage design και tests.

### SEC-016 — Περιορισμένο Patient Portal και AMKA privacy

- **Περιγραφή:** Το portal επιτρέπει μόνο τα προβλεπόμενα appointment workflows, χωρίς clinical records ή διαρροή ταυτότητας.
- **Προτεραιότητα / κατάσταση:** P1 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Upcoming appointments, eligible cancellation/rescheduling περιορίζονται στον authenticated patient και επιτρεπόμενο clinic context. Medical-record access απορρίπτεται. AMKA/account existence δεν αποκαλύπτονται από public responses, URLs ή logs. Ορίζονται eligibility κανόνες πριν τη διάθεση.
- **Evidence / κενό:** `FR-PORTAL-001`–`FR-PORTAL-006`. Δεν υπάρχουν endpoints ή tests.

### SEC-017 — Input validation και resource limits

- **Περιγραφή:** Κάθε input και κατανάλωση πόρων πρέπει να περιορίζεται με εγκεκριμένους κανόνες.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Εφαρμόζονται field lengths, password byte limits, request sizes και pagination bounds· upload limits όπου υπάρχουν uploads. Boundary/malformed input tests παράγουν ελεγχόμενα errors χωρίς sensitive payload reflection.
- **Evidence / κενό:** E01/E03: `EmailStr`, clinic path bounds. T01/T04 καλύπτουν JWT/clinic boundaries. Δεν υπάρχουν πλήρη schema/body/resource limits.

### SEC-018 — Ασφάλεια database access και ακεραιότητα

- **Περιγραφή:** Queries πρέπει να είναι παραμετροποιημένα, οι σχέσεις έγκυρες και τα DB privileges ελάχιστα.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Δεν υπάρχει concatenation μη έμπιστου input σε SQL. Constraints εμποδίζουν invalid memberships/roles και μελλοντικές cross-clinic σχέσεις. Runtime DB role δεν αποκτά migration/admin privileges. Schema changes συνοδεύονται από reviewed Alembic migrations και upgrade/downgrade verification όπου πρακτικό.
- **Evidence / κενό:** E04/E05/E10, T07: ORM, FKs, unique constraints, role enum. Least-privilege DB setup και tenant-consistent domain relationships δεν τεκμηριώνονται. Δεν εκτελέστηκαν migrations εδώ.

### SEC-019 — Ελαχιστοποίηση responses και ασφαλή errors

- **Περιγραφή:** APIs και UI πρέπει να αποκαλύπτουν μόνο τα αναγκαία δεδομένα, χωρίς τεχνικά ή authentication secrets.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Explicit response schemas αποκλείουν hashes και περιττά sensitive fields. Error tests καλύπτουν validation, DB failure και concurrent registration χωρίς SQL, stack traces, credentials ή πλήρες medical content. Tokens επιστρέφονται μόνο όπου απαιτείται από το authentication contract.
- **Evidence / κενό:** E01/E07, T03/T09/T10: public user fields και σταθερά UI error messages. Δεν υπάρχει συστηματική backend error redaction· DB exception propagation tests δεν αποδεικνύουν ασφαλή logs/responses.

### SEC-020 — Rate limiting και abuse prevention

- **Περιγραφή:** Login, registration, recovery, OTP και ευαίσθητα/δαπανηρά APIs πρέπει να έχουν εγκεκριμένους abuse controls.
- **Προτεραιότητα / κατάσταση:** P0 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Τεκμηριώνονται account/IP/session keys, thresholds, windows και proxy trust. Υπερβάσεις απορρίπτονται ελεγχόμενα. Concurrent και multi-instance tests επιβεβαιώνουν τη διατήρηση ορίων χωρίς ανεξέλεγκτο account-lockout abuse.
- **Evidence / κενό:** Προδιαγραφή §24. Δεν βρέθηκαν limiter implementation ή tests.

### SEC-021 — Audit trail και λογοδοσία

- **Περιγραφή:** Σημαντικές security και clinical ενέργειες πρέπει να αφήνουν προστατευμένο audit evidence.
- **Προτεραιότητα / κατάσταση:** P0 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Εγκεκριμένο event catalogue καλύπτει role/account changes, sensitive access, mutations και exports. Καταγράφονται actor, Clinic, action, target identifier, time και outcome χωρίς πλήρες sensitive content. Tests ελέγχουν δημιουργία events και απαγόρευση μη εξουσιοδοτημένης πρόσβασης/αλλοίωσης.
- **Evidence / κενό:** `NFR-009`, προδιαγραφή §24. Timestamps μοντέλων δεν αποτελούν πλήρες audit trail· δεν υπάρχει σχετική implementation/test evidence.

### SEC-022 — Logging χωρίς sensitive leakage

- **Περιγραφή:** Application, access και error logs πρέπει να ελαχιστοποιούν και να αποκρύπτουν sensitive δεδομένα.
- **Προτεραιότητα / κατάσταση:** P0 · Προγραμματισμένο.
- **Κριτήρια αποδοχής:** Log-capture tests σε επιτυχίες/αποτυχίες δεν βρίσκουν passwords, hashes, tokens, OTPs, πλήρη AMKA ή medical content. Καθορίζονται retention, πρόσβαση, redaction και χειρισμός SQL parameters/exception details.
- **Evidence / κενό:** E09: γενικό Alembic logging. Δεν υπάρχει application redaction policy ή test evidence. Απουσία explicit logging δεν αποδεικνύει ασφαλή default server logs.

### SEC-023 — Secrets και ασφαλές configuration

- **Περιγραφή:** Μυστικά πρέπει να παρέχονται εκτός κώδικα, με ασφαλή production validation και rotation.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό.
- **Κριτήρια αποδοχής:** Production configuration απορρίπτει missing/placeholder secrets και development DB defaults. Secret storage, access και rotation τεκμηριώνονται. Νέες απαιτούμενες μεταβλητές περιλαμβάνονται χωρίς πραγματικές τιμές στο `.env.example`. Δεν μεταφέρονται backend secrets σε frontend bundles ή build contexts.
- **Evidence / κενό:** E02/E08/E09: environment settings, απαιτούμενο `SECRET_KEY` με minimum length, example και βασικά ignore rules. Υπάρχουν development DB fallbacks· δεν υπάρχει production gate ή rotation runbook. Το `API_PREFIX` δεν εφαρμόζεται στο router inclusion· πραγματικές διαδρομές είναι `/auth/*`.

### SEC-024 — Ασφαλής μεταφορά

- **Περιγραφή:** Δημόσια παραγωγική επικοινωνία και sensitive service connections πρέπει να προστατεύονται με εγκεκριμένο transport configuration.
- **Προτεραιότητα / κατάσταση:** P0 · Άγνωστο για production.
- **Κριτήρια αποδοχής:** Deployment verification αποδεικνύει HTTPS, κατάλληλο HTTP handling, εγκεκριμένο TLS/HSTS και ασφαλή proxy trust. Αξιολογούνται API–DB και provider links σύμφωνα με το δίκτυο και την απειλή.
- **Evidence / κενό:** E08 περιγράφει development HTTP servers. Δεν τεκμηριώνονται TLS termination, certificates ή live infrastructure tests.

### SEC-025 — Browser boundary, origins και injection

- **Περιγραφή:** Η πολιτική origins, rendering και CSRF πρέπει να αντιστοιχεί στον επιλεγμένο authentication μηχανισμό.
- **Προτεραιότητα / κατάσταση:** P1 · Μερικό.
- **Κριτήρια αποδοχής:** Καθορίζονται same-origin/CORS policy, trusted hosts και security headers/CSP. Μη επιτρεπόμενα origins δεν λαμβάνουν εξουσιοδοτημένα responses. Ελέγχεται ασφαλές rendering μη έμπιστων τιμών. Αν εισαχθεί cookie authentication, ορίζονται cookie flags και CSRF controls πριν τη χρήση του.
- **Evidence / κενό:** E06/E07/E08: React rendering, relative `/auth/*` requests και Vite proxy. Δεν τεκμηριώνεται production header/origin policy. Δεν θεωρείται ότι η απουσία CORS middleware επιτρέπει όλα τα origins ή ότι λύνει το authorization.

### SEC-026 — Production deployment hardening

- **Περιγραφή:** Η παραγωγή πρέπει να έχει ξεχωριστό, ελεγχόμενο deployment από το development/demo setup.
- **Προτεραιότητα / κατάσταση:** P0 · Μερικό μόνο ως containerized development setup.
- **Κριτήρια αποδοχής:** Δεν χρησιμοποιούνται reload/Vite development servers στην παραγωγή. Εφαρμόζονται non-root execution, περιορισμένα network ports/volumes και ελεγμένα image build contexts. Docs και health endpoints έχουν εγκεκριμένη exposure policy. Configuration review αποδεικνύει ότι η DB δεν είναι δημόσια προσβάσιμη.
- **Evidence / κενό:** E08: development servers, host-published DB/backend ports και bind mounts· δεν δηλώνεται non-root user. Δεν βρέθηκαν Docker ignore files ή production deployment runbook.

### SEC-027 — Dependency assurance

- **Περιγραφή:** Οι εξαρτήσεις και τα images πρέπει να είναι αναπαραγώγιμα και να ελέγχονται για γνωστές ευπάθειες.
- **Προτεραιότητα / κατάσταση:** P1 · Μερικό.
- **Κριτήρια αποδοχής:** Εφαρμόζεται εγκεκριμένη pinning/locking στρατηγική, επαναλήψιμο build και καταγεγραμμένος vulnerability έλεγχος. Ορίζονται remediation deadlines και release blocking policy. Exceptions έχουν υπεύθυνο και αιτιολόγηση.
- **Evidence / κενό:** E11: frontend manifest/lockfile και κυρίως unpinned backend dependencies. Δεν βρέθηκε CI security gate. Δεν έγινε dependency audit στο SECURITY-00A και δεν δηλώνεται ότι συγκεκριμένη dependency είναι ευάλωτη.

### SEC-028 — Backups, encryption και recovery

- **Περιγραφή:** Πριν από πραγματικά δεδομένα πρέπει να εξασφαλίζεται ασφαλής ανάκτηση και προστασία των αποθηκευμένων αντιγράφων.
- **Προτεραιότητα / κατάσταση:** P0 · Άγνωστο επιχειρησιακά· backup/recovery αναφέρονται ως μελλοντική επέκταση στην προδιαγραφή §31.
- **Κριτήρια αποδοχής:** Εγκρίνονται RPO/RTO, retention, encryption at rest, key custody και περιορισμός backup access. Καταγράφεται επιτυχές restore σε απομονωμένο περιβάλλον με ελέγχους ακεραιότητας και tenant isolation. Η διαγραφή/λήξη αντιγράφων συνδέεται με την data-lifecycle πολιτική.
- **Evidence / κενό:** E08: persistent volume, όχι αποδεδειγμένο backup. Δεν υπάρχουν restore tests/runbook. Η ένταξη backup/recovery ως production blocker απαιτεί μελλοντική εναρμόνιση της προδιαγραφής πριν από σχετική υλοποίηση.

### SEC-029 — Incident response

- **Περιγραφή:** Πρέπει να υπάρχει καθορισμένη διαδικασία αναγνώρισης, περιορισμού και αποκατάστασης περιστατικών.
- **Προτεραιότητα / κατάσταση:** P0 · Άγνωστο.
- **Κριτήρια αποδοχής:** Ορίζονται υπεύθυνοι, escalation, διαφύλαξη evidence, credential rotation, recovery και διαδικασία αξιολόγησης γνωστοποιήσεων. Καταγράφεται tabletop exercise με διορθωτικές ενέργειες.
- **Evidence / κενό:** Δεν βρέθηκε incident runbook ή exercise evidence. Δεν αποδίδονται νομικές προθεσμίες χωρίς εφαρμοστέα αξιολόγηση.

### SEC-030 — Privacy και data lifecycle

- **Περιγραφή:** Συλλογή, χρήση, πρόσβαση, retention, export και διαγραφή πρέπει να εξυπηρετούν καθορισμένους σκοπούς με ελαχιστοποίηση.
- **Προτεραιότητα / κατάσταση:** P0 · Άγνωστο ως λειτουργική πολιτική.
- **Κριτήρια αποδοχής:** Εγκρίνονται data inventory και retention ανά κατηγορία, ασφαλείς διαδικασίες αιτημάτων πρόσβασης/διόρθωσης/export/διαγραφής και χειρισμός νόμιμων περιορισμών. Tests εμποδίζουν cross-clinic exports και μη εξουσιοδοτημένη διαγραφή. Analytics/intelligent features έχουν τεκμηριωμένα inputs και σκοπούς.
- **Evidence / κενό:** `NFR-002`, προδιαγραφή §§17, 24. Δεν υπάρχουν αντίστοιχες διαδικασίες ή domain tests. Μέχρι το production gate επιτρέπονται μόνο συνθετικά δεδομένα.

### SEC-031 — Διακυβέρνηση και αξιολόγηση πραγματικών δεδομένων

- **Περιγραφή:** Η μετάβαση σε πραγματική χρήση απαιτεί τεκμηρίωση ευθυνών, παρόχων και εφαρμοστέων υποχρεώσεων προστασίας δεδομένων.
- **Προτεραιότητα / κατάσταση:** P0 · Άγνωστο· τρέχουσα άδεια περιορίζεται σε synthetic-data demo.
- **Κριτήρια αποδοχής:** Πριν από παραγωγή εγκρίνονται controller/processor responsibilities, σκοποί/νομική βάση, όρος επεξεργασίας health data, ενημερώσεις, provider agreements, τοποθεσίες/διαβιβάσεις και αξιολόγηση ανάγκης DPIA/DPO. Αρμόδιοι εξετάζουν τις ελληνικές healthcare/retention υποχρεώσεις. Υπάρχει ρητή νέα απόφαση εισαγωγής πραγματικών δεδομένων.
- **Evidence / κενό:** Υπάρχουν γενικές privacy/security απαιτήσεις, όχι αποδεδειγμένη νομική συμμόρφωση ή operational governance evidence.

### SEC-032 — Verification και ελεγχόμενη αποδέσμευση

- **Περιγραφή:** Κάθε απαίτηση πρέπει να έχει traceability σε κώδικα, tests ή ελέγξιμη επιχειρησιακή διαδικασία.
- **Προτεραιότητα / κατάσταση:** P1 · Μερικό.
- **Κριτήρια αποδοχής:** Κάθε νέο protected endpoint έχει authentication, role και cross-tenant negative tests. Release evidence περιλαμβάνει commit, περιβάλλον, εκτελεσμένες εντολές, αποτελέσματα και περιορισμούς. Ανοικτές απαιτήσεις δεν δηλώνονται ως completed χωρίς evidence· exceptions δεν επιτρέπουν παράκαμψη της τρέχουσας απαγόρευσης πραγματικών δεδομένων.
- **Evidence / κενό:** T01–T11 παρέχουν υπάρχον test code, E12 προστατεύει το test DB target και χρησιμοποιεί rollback. Δεν υπάρχει test-run evidence αυτής της εργασίας ή ολοκληρωμένο release/security gate automation.

## 7. Εγκεκριμένο RBAC matrix

Το matrix περιγράφει **permissions**, όχι ήδη διαθέσιμες domain λειτουργίες. Πηγή υλοποίησης: E03. Υπάρχουσα test evidence: T05/T06.

| Permission | OWNER | DOCTOR | SECRETARY |
|---|:---:|:---:|:---:|
| `patients.read` | Ναι | Ναι | Ναι |
| `patients.create` | Ναι | Ναι | Ναι |
| `patients.update_basic` | Ναι | Ναι | Ναι |
| `patients.delete` | Ναι | Όχι | Όχι |
| `medical_records.read` | Ναι | Ναι | Όχι |
| `medical_records.write` | Ναι | Ναι | Όχι |
| `appointments.read` | Ναι | Ναι | Ναι |
| `appointments.manage` | Ναι | Ναι | Ναι |
| `payments.read` | Ναι | Όχι | Ναι |
| `payments.manage` | Ναι | Όχι | Ναι |
| `clinic.manage_members` | Ναι | Όχι | Όχι |
| `clinic.settings` | Ναι | Όχι | Όχι |

Ο OWNER έχει όλες τις permissions **αποκλειστικά εντός της δικής του Clinic**. Το `is_superuser` δεν αποτελεί bypass. Membership χωρίς roles δεν έχει permissions, παρότι μπορεί να επιλυθεί ως έγκυρο context. DOCTOR + SECRETARY στην ίδια Clinic λαμβάνει την ένωση των δύο στηλών, χωρίς OWNER-only permissions. DOCTOR στην Clinic A και SECRETARY στην Clinic B δεν συνδυάζονται.

Η πρόσβαση OWNER σε clinical records είναι ρητή απόφαση, ακόμη και αν δεν είναι DOCTOR. Αυξάνει τον αριθμό προσώπων με πρόσβαση σε ιδιαίτερα ευαίσθητο περιεχόμενο και απαιτεί ενημέρωση πολιτικής ιδιωτικότητας, ασφαλές provisioning, audit trail και αρνητικά cross-clinic tests. Δεν εγκρίνει νομικά την πραγματική επεξεργασία. Η παρούσα εργασία δεν εισάγει εξαιρέσεις ή νέο ρόλο για να περιορίσει αυτή την απόφαση.

Clinic context και RBAC είναι υλοποιημένα foundations που ελέγχονται μέσω **test-only routes**. T04/T06 ελέγχουν επίσης ότι αυτές οι διαδρομές δεν καταχωρίζονται στην production application. Resource-level Patient isolation και clinical endpoint enforcement δεν έχουν υλοποιηθεί.

## 8. Απειλές και σχετικοί έλεγχοι

| Απειλή / σενάριο | Συνέπεια | Σχετικές απαιτήσεις |
|---|---|---|
| Credential stuffing, enumeration, unbounded registration | Κατάληψη λογαριασμών, κατάχρηση πόρων | SEC-001–SEC-005, SEC-017, SEC-020 |
| Κλοπή/replay JWT μετά από logout ή XSS | Μη εξουσιοδοτημένη πρόσβαση όσο το token γίνεται δεκτό | SEC-006–SEC-009, SEC-023–SEC-025 |
| Αλλαγή `clinic_id` ή resource ID | Διαρροή/μεταβολή δεδομένων άλλου ιατρείου | SEC-010–SEC-013, SEC-018, SEC-032 |
| Συνδυασμός roles διαφορετικών Clinics | Privilege escalation εκτός εγκεκριμένου context | SEC-010–SEC-013 |
| Κατάχρηση OWNER ή εσφαλμένη role assignment | Ευρεία clinical πρόσβαση εντός tenant | SEC-001, SEC-011, SEC-013, SEC-021, SEC-030 |
| OTP brute force, replay ή λανθασμένο contact destination | Πρόσβαση σε ραντεβού άλλου ασθενούς | SEC-014–SEC-016, SEC-020 |
| AMKA lookup, logs, errors, reminders ή analytics leakage | Αποκάλυψη ταυτότητας και σχέσης με περίθαλψη | SEC-016, SEC-019, SEC-021–SEC-022, SEC-030 |
| SQL/injection ή cross-clinic object relationships | Παραβίαση ακεραιότητας και απομόνωσης | SEC-012, SEC-017–SEC-018, SEC-025 |
| Δημόσια DB, development server, exposed secret ή dependency flaw | Παραβίαση εφαρμογής/υποδομής | SEC-023–SEC-027 |
| Απώλεια DB ή μη ελεγμένο restore | Απώλεια αρχείων και διακοπή λειτουργίας | SEC-018, SEC-028–SEC-029 |
| Μη εγκεκριμένα exports ή χρήση ιστορικών δεδομένων σε intelligent features | Δευτερογενής χρήση πέρα από τον σκοπό | SEC-012, SEC-019, SEC-030–SEC-031 |

Η παρουσία controls στο repository δεν μηδενίζει τις απειλές. Ειδικά metadata ραντεβού και πληρωμών μπορούν να αποκαλύψουν πληροφορίες υγείας χωρίς medical notes. Τα intelligent features παραμένουν υποβοηθητικά και δεν λαμβάνουν αυτόνομες ιατρικές αποφάσεις, σύμφωνα με την προδιαγραφή §17.

## 9. Release gates

### 9.1 Gate ανάπτυξης και επίδειξης με συνθετικά δεδομένα

Πριν από κάθε επίδειξη πρέπει να επιβεβαιώνονται:

- Dataset, seed data, screenshots, exports και logs περιέχουν μόνο συνθετικά στοιχεία ασθενών. Πραγματικά credentials παραμένουν προστατευμένα.
- Το περιβάλλον είναι ελεγχόμενο, χωρίς δημόσια παραγωγική έκθεση· network access και δημοσιευμένα ports έχουν ελεγχθεί.
- Παρουσιάζονται μόνο υλοποιημένες λειτουργίες και τα γνωστά gaps δηλώνονται. Test-only routes δεν διατίθενται ως application features.
- Για το συγκεκριμένο release καταγράφονται relevant test results, commit και περιβάλλον. Η παρούσα τεκμηρίωση δεν υποκαθιστά αυτόν τον έλεγχο.
- Τα gaps που γίνονται αποδεκτά για την ακαδημαϊκή επίδειξη καταγράφονται μαζί με τον περιορισμό σε synthetic data.

Το gate δεν απαιτεί να παρουσιαστούν ως ολοκληρωμένα όλα τα production controls. Δεν επιτρέπει χρήση πραγματικών δεδομένων ή δημόσια παραγωγή, ακόμη και αν τα tests περάσουν. Το SECURITY-00A δεν πιστοποιεί ότι εκτελέστηκε συγκεκριμένο demo gate.

### 9.2 Gate πριν από πραγματικά δεδομένα ή δημόσια παραγωγή

Η μετάβαση παραμένει απαγορευμένη μέχρι να ολοκληρωθούν και να ελεγχθούν ανεξάρτητα:

- Όλες οι P0 απαιτήσεις και οι P1 απαιτήσεις των λειτουργιών που θα διατεθούν, με evidence έναντι κάθε acceptance criterion.
- Resource-level tenant isolation σε πραγματικά domain endpoints, μαζί με tests για OWNER, πολλαπλές memberships, αναζητήσεις, aggregates και exports.
- Εγκεκριμένο staff lifecycle, authentication/session policies, abuse controls και ασφαλές error/logging handling.
- Production deployment review: secrets, TLS, network/DB privileges, containers, dependency checks και origin/browser policy.
- Auditability, backup/restore verification, incident response και κατανομή επιχειρησιακών ευθυνών.
- Privacy/legal assessment, απαιτούμενη τεκμηρίωση και καθορισμός retention/providers/transfers, χωρίς αυτόματη υπόθεση GDPR συμμόρφωσης.
- Επίλυση ή τεκμηριωμένη απόφαση για κάθε σχετική ανοικτή επιλογή και εναρμόνιση προδιαγραφής όπου απαιτείται.
- Ρητή νέα έγκριση από τον project owner για τον συγκεκριμένο σκοπό, deployment και εισαγωγή πραγματικών δεδομένων.

Το gate είναι διαδικασία στόχου, όχι υλοποιημένος αυτοματισμός ή τρέχουσα εξουσιοδότηση. Η αναφορά της προδιαγραφής §31 σε μελλοντικά backups δεν αποτελεί απαλλαγή από τις απαιτήσεις recovery πριν από πραγματική χρήση.

## 10. Requirement-to-test traceability

### 10.1 Κατάλογος υπάρχουσας test evidence

| ID | Αρχείο | Ενδεικτικά επιθεωρημένα assertions |
|---|---|---|
| T01 | [test_auth.py](../../backend/tests/test_auth.py) | Login subject, missing/invalid claims, invalid signature, expired/invalid expiration. Το password verification γίνεται mock στο login test. |
| T02 | [test_current_user.py](../../backend/tests/test_current_user.py) | Active user, invalid credentials χωρίς lookup, nonexistent/inactive user, DB failure propagation. |
| T03 | [test_auth_me.py](../../backend/tests/test_auth_me.py) | Public user fields χωρίς hash, 401 credentials, 403 inactive user. |
| T04 | [test_clinic_context.py](../../backend/tests/test_clinic_context.py) | Multiple roles, ανεξάρτητα contexts, ισοδύναμα 404, bounds, no superuser bypass, DB changes με ίδιο JWT, test route εκτός production. |
| T05 | [test_permissions.py](../../backend/tests/test_permissions.py) | Ακριβές permission catalogue/matrix, OWNER all permissions, multi-role union, empty roles. |
| T06 | [test_clinic_authorization.py](../../backend/tests/test_clinic_authorization.py) | Request matrix σε test-only routes, cross-clinic role isolation, zero roles, no bypass, role changes με ίδιο JWT, test routes εκτός production. |
| T07 | [test_clinic_membership_constraints.py](../../backend/tests/test_clinic_membership_constraints.py) | Unique memberships/roles, foreign keys, multiple roles, ακριβές enum και invalid enum rejection. |
| T08 | [auth-provider.test.tsx](../../frontend/tests/auth-provider.test.tsx) | Login→me sequence, failures, local logout, pending request deduplication και stale response handling. |
| T09 | [api.test.mjs](../../frontend/tests/api.test.mjs) | Encoded login request, bearer header, status classification και σταθερά error messages. |
| T10 | [login-page.test.tsx](../../frontend/tests/login-page.test.tsx) | Native form semantics, safe UI errors, password clearing, token/password εκτός DOM. |
| T11 | [routing.test.tsx](../../frontend/tests/routing.test.tsx) | Protected UI navigation, logout, fresh provider χωρίς memory authentication. |

### 10.2 Κάλυψη απαιτήσεων και ελλείψεις verification

| Απαίτηση | Υπάρχουσα evidence | Πρόσθετη verification που απαιτείται |
|---|---|---|
| SEC-001 | Καμία ειδική | Bootstrap/invitations και unauthorized role assignment tests. |
| SEC-002 | T01, μόνο mocked verification | Real hashing/verification και input byte boundaries. |
| SEC-003 | T02, T03, T06 | Login denial inactive user, activation lifecycle. |
| SEC-004 | T09/T10 για ασφαλή client errors | Failed login, registration enumeration, timing assessment. |
| SEC-005 | Καμία | Recovery/replay/password-change policy tests ή approved exclusion. |
| SEC-006 | T01–T03 | Disallowed algorithm και πλήρες approved token contract. |
| SEC-007 | T01, T03, T08 | Expiration UX, replay/revocation και credential-change behavior. |
| SEC-008 | T08, T10, T11 | Συστηματική επιβεβαίωση storage/URL handling σε νέες ροές. |
| SEC-009 | T02, T03, T11 μόνο για UI | Endpoint inventory/allowlist και authentication tests για όλα τα νέα APIs. |
| SEC-010 | T04 | Ενσωμάτωση dependency σε production clinic endpoints. |
| SEC-011 | T05, T06 | RBAC tests σε πραγματικά domain endpoints. |
| SEC-012 | T04/T06 μόνο για membership context | Patient/resource CRUD, links, search, exports και analytics isolation. |
| SEC-013 | T05/T06 μόνο για permissions | Clinical endpoint/field tests, OWNER-only και cross-clinic denial. |
| SEC-014 | Καμία | Staff/patient session separation tests. |
| SEC-015 | Καμία | OTP expiry, attempts, replay, concurrency και destination binding. |
| SEC-016 | Καμία | Portal scope, eligibility, cross-patient/clinic denial και enumeration tests. |
| SEC-017 | T01, T04 για περιορισμένα boundaries | Schema/body/pagination/upload limits και error reflection tests. |
| SEC-018 | T07 | Domain constraints, query review, runtime DB privileges και migration verification. |
| SEC-019 | T03, T09, T10 | Backend validation/DB/concurrent-registration failure sanitization. |
| SEC-020 | Καμία | Throttle thresholds, concurrent/multi-instance enforcement. |
| SEC-021 | Καμία | Audit event generation, access και tampering tests. |
| SEC-022 | Καμία | Captured application/access/error log leakage tests. |
| SEC-023 | Καμία ειδική | Production settings failure cases, secret/build review και rotation exercise. |
| SEC-024 | Καμία | Deployed TLS/proxy/DB transport verification. |
| SEC-025 | T10 μόνο για περιορισμένο UI leakage | Origin, headers, unsafe rendering και conditional cookie/CSRF tests. |
| SEC-026 | Καμία | Deployment/network/container configuration review. |
| SEC-027 | Καμία ειδική | Reproducible builds και καταγεγραμμένα vulnerability scan results. |
| SEC-028 | Καμία | Isolated restore, integrity, tenant isolation και RPO/RTO evidence. |
| SEC-029 | Καμία | Incident tabletop και διορθωτικές ενέργειες. |
| SEC-030 | Καμία ειδική | Data inventory, retention/export/deletion workflow tests. |
| SEC-031 | Καμία | Governance/privacy assessment και ρητή production authorization. |
| SEC-032 | T01–T11 ως test code, E12 | Καταγεγραμμένες εκτελέσεις ανά release και ολοκληρωμένη traceability review. |

Ο πίνακας δεν δηλώνει πλήρη κάλυψη επειδή αναφέρει ένα test. Δεν εκτελέστηκαν αυτά τα tests κατά την παρούσα εργασία. Το E12 περιορίζει ρητά το test database target και χρησιμοποιεί transaction rollback· αυτό δεν αποτελεί απόδειξη production backup ή tenant isolation όλων των resources.

## 11. Ανοικτές αποφάσεις, κίνδυνοι και privacy assessment

Οι αποφάσεις synthetic-only χρήσης, απαγόρευσης παραγωγής, OWNER permissions και clinic-local role union έχουν κλείσει για το παρόν scope. Παραμένουν:

| Απόφαση / κίνδυνος | Σχετικές απαιτήσεις | Πότε πρέπει να κλείσει |
|---|---|---|
| Bootstrap authority, invitation expiry/reuse, activation και μετάβαση από public registration | SEC-001, SEC-003 | Πριν διατεθεί νέο onboarding και οπωσδήποτε πριν παραγωγή. |
| Password bounds/work factor, recovery, MFA απόφαση και credential-change invalidation | SEC-002, SEC-005, SEC-007 | Πριν το αντίστοιχο workflow και το production gate. |
| Token lifetime/idle/concurrency/revocation, issuer/audience και patient token purpose | SEC-006, SEC-007, SEC-014 | Πριν ολοκλήρωση session/portal design. |
| Doctor assignment restrictions, patient deletion policy και audit event catalogue | SEC-012, SEC-013, SEC-021 | Πριν Patient/MedicalRecord endpoints. Το OWNER clinical access δεν είναι ανοικτό θέμα. |
| AMKA clinic lookup, verified destination, OTP provider/channel, expiry/entropy/attempt/resend limits | SEC-014–SEC-016, SEC-020 | Πριν Patient Portal implementation. |
| Request/throttle limits, log retention και security alert handling | SEC-017, SEC-020–SEC-022 | Πριν σχετική διάθεση· production blockers όπου εφαρμόζονται. |
| Hosting region, TLS/proxy/headers, DB role/network/encryption, secret/key custody | SEC-018, SEC-023–SEC-026 | Πριν επιλογή production deployment. |
| Dependency remediation policy, backup retention/RPO/RTO και incident owners | SEC-027–SEC-029 | Πριν production-readiness review. |
| Data inventory, retention και αιτήματα δικαιωμάτων, providers/transfers, controller/processor responsibilities | SEC-030, SEC-031 | Πριν οποιαδήποτε πραγματικά δεδομένα. |
| Scope παραγωγικών λειτουργιών, reviewers και specification alignment για backup/recovery | SEC-028, SEC-032 | Πριν production gate· δεν απαιτείται αλλαγή άλλου εγγράφου σε αυτό το task. |

Δεν εισάγονται αυθαίρετα αριθμητικά thresholds. Οι υφιστάμενες τιμές στον κώδικα καταγράφονται ως evidence, όχι ως απόφαση παραγωγικής καταλληλότητας. Public registration, inactive-user token issuance, έλλειψη revocation/rate limiting, μη υλοποιημένη Patient isolation και άγνωστα operational controls παραμένουν ρητοί κίνδυνοι.

Για μελλοντική πραγματική επεξεργασία απαιτείται ειδική αξιολόγηση της εφαρμογής του GDPR: σκοπός και lawful basis, προϋπόθεση επεξεργασίας health data, ελαχιστοποίηση/retention, ενημέρωση και δικαιώματα, privacy by design, processor responsibilities, ασφάλεια/recovery, breach handling και ανάγκη DPIA/DPO. Σχετικές περιοχές είναι τα άρθρα 5–6, 9, 12–22, 25, 28, 30, 32–37 και οι διεθνείς διαβιβάσεις όπου εφαρμόζονται. Πρέπει επίσης να εξεταστούν οι εφαρμοστέοι ελληνικοί κανόνες ιατρικών αρχείων και επαγγελματικού απορρήτου από αρμόδιους. Δεν τεκμαίρεται ότι consent είναι η κατάλληλη βάση ή ότι τα τεχνικά controls αρκούν για συμμόρφωση. Πρωτογενής αναφορά: [Κανονισμός (ΕΕ) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/ell).

## 12. Ιστορικό εκδόσεων

| Έκδοση | Ημερομηνία | Μεταβολή |
|---|---|---|
| 1.0 | 2026-10-30 | SECURITY-00A: αρχική καταγραφή SEC-001–SEC-032, εγκεκριμένου RBAC, synthetic-only scope, evidence/traceability, κινδύνων και διακριτών release gates. Δεν συνοδεύεται από εκτέλεση application tests ή production approval. |
