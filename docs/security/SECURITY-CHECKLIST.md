# Checklist Ασφάλειας — med-app

## 1. Στοιχεία εγγράφου, baseline και σκοπός

| Πεδίο | Τιμή |
|---|---|
| Εργασία | SECURITY-00D |
| Έκδοση / ημερομηνία | 1.0 / 2026-10-31 |
| Κατάσταση | Αρχικό implementation baseline και πρακτικό σχέδιο verification· όχι release approval |
| Branch | `feature/clinic-authorization` |
| Baseline commit | `0bb9821dde8ac0ae63e793594174ffb2a9e98520` |
| Βάση σχεδιασμού | Ολοκληρωμένη read-only επιθεώρηση SECURITY-00D και στοχευμένη διασταύρωση repository evidence |
| Προδιαγραφή | [System Specification v1.0](../system-specification.md), ιδίως §§5–6, 19–24, 26–27 και 31 |
| Requirements | [SECURITY-REQUIREMENTS.md](SECURITY-REQUIREMENTS.md), SEC-001 έως SEC-032 |
| Threat model | [THREAT-MODEL.md](THREAT-MODEL.md), TM-001 έως TM-018 |
| Architecture | [SECURITY-ARCHITECTURE.md](SECURITY-ARCHITECTURE.md) |

Σκοπός είναι να μετατραπούν οι απαιτήσεις και οι αρχιτεκτονικοί έλεγχοι σε συγκεκριμένες ερωτήσεις Ναι/Όχι. Τα 48 stable CHK IDs διατηρούν το scope, τις προτεραιότητες και τις implementation καταστάσεις της επιθεώρησης. Η μετάφραση των ερωτήσεων στα ελληνικά δεν αλλάζει το νόημά τους. Τα παλαιότερα baseline commits των τριών security εγγράφων παραμένουν ιστορικές αναφορές, όχι ασυμφωνία.

**Επιτρέπονται μόνο ανάπτυξη και ελεγχόμενη ακαδημαϊκή επίδειξη με συνθετικά δεδομένα. Πραγματικά δεδομένα ασθενών και δημόσια παραγωγική εγκατάσταση δεν είναι εξουσιοδοτημένα. Η συμμόρφωση με τον GDPR δεν έχει τεκμηριωθεί.**

Η αρχιτεκτονική υποστηρίζει πιθανή μελλοντική πραγματική χρήση, υπό ξεχωριστό production-readiness gate και νέα ρητή έγκριση. Η απλή ψευδωνυμοποίηση πραγματικών φακέλων δεν τους μετατρέπει σε συνθετικά δεδομένα. Πραγματικά developer credentials, signing keys και υποδομή παραμένουν προστατευόμενα assets ακόμη και στο synthetic demo.

## 2. Οδηγίες χρήσης: implementation status και verification result

Τα δύο πεδία είναι ανεξάρτητα. Το implementation status περιγράφει τι υποστηρίζει το repository evidence για την ακριβή ερώτηση. Το verification result περιγράφει αν έγινε επαρκής έλεγχος για συγκεκριμένο release και περιβάλλον.

| Implementation status | Σημασία |
|---|---|
| Implemented | Υπάρχει πραγματικός κώδικας/constraint για το δηλωμένο περιορισμένο πεδίο. Δεν σημαίνει επιτυχές test run ή παραγωγική ετοιμότητα. |
| Partial | Υπάρχει τμήμα του control, αλλά όχι πλήρης κάλυψη της ερώτησης. |
| Planned | Απαιτούμενη ή εγκεκριμένη μελλοντική λειτουργία χωρίς implementation evidence. |
| Unknown | Δεν υπάρχουν επαρκή στοιχεία για operational εφαρμογή ή επαλήθευση. |
| Not Applicable | Μόνο με τεκμηριωμένο λόγο ότι το control δεν αφορά το εξεταζόμενο scope. Δεν χρησιμοποιείται για να κρύψει απουσία απαιτούμενου control. |

| Verification result | Σημασία |
|---|---|
| Yes | Η ερώτηση απαντήθηκε θετικά με επαρκές, συγκεκριμένο release evidence. |
| No | Ο έλεγχος εκτελέστηκε και απέδειξε ότι η ερώτηση δεν ικανοποιείται. |
| Not verified | Δεν έγινε το απαιτούμενο test/operational verification ή λείπει επαρκές release evidence. Δεν σημαίνει Yes. |
| Not Applicable | Εγκεκριμένος και καταγεγραμμένος αποκλεισμός για το συγκεκριμένο release, όχι αυτόματη επιτυχία. |

**Όλα τα αρχικά verification results είναι `Not verified`.** Ο κώδικας και τα test sources επιθεωρήθηκαν, αλλά δεν εκτελέστηκαν application tests, migrations ή operational checks κατά το SECURITY-00D. Οι δομικοί έλεγχοι του παρόντος Markdown δεν επαληθεύουν τα application controls. Δεν επιθεωρήθηκαν πραγματικά secret values, live hosting ή εγκατεστημένες εξαρτήσεις για vulnerabilities.

Για κάθε release αντιγράφονται τα applicable CHK IDs στο record της ενότητας 10. Συμπληρώνονται πραγματικά αποτελέσματα, reviewer και evidence, χωρίς να αλλάζει αναδρομικά το ιστορικό baseline. Κάθε νέα edition μπορεί να ενημερώσει το implementation status μόνο με νέο code/operational evidence.

Ελλείποντα Patient APIs ή OTP δεν είναι Not Applicable στο implementation baseline: είναι Planned. Μια μη διαθέσιμη λειτουργία μπορεί να αποκλειστεί από ένα συγκεκριμένο release με αιτιολόγηση. Αν όμως διατίθεται η λειτουργία, δεν επιτρέπεται εξαίρεση του απαραίτητου security control με αυτόν τον τρόπο. Δεν προεπιλέγονται checkboxes από documentation ή test filenames.

## 3. Προτεραιότητες και release applicability

| Priority | Ερμηνεία |
|---|---|
| P0 | Υποχρεωτική επίλυση πριν από πραγματικά δεδομένα ή δημόσια παραγωγή, σύμφωνα με τις σχετικές SEC απαιτήσεις. |
| P1 | Υποχρεωτική ολοκλήρωση πριν τη διάθεση της σχετικής λειτουργίας. Αν περιλαμβάνεται στην παραγωγή, είναι επίσης blocker. |
| P2 | Πρόσθετη ενίσχυση μετά τα βασικά gates, μόνο με τεκμηριωμένη ανάγκη. Δεν απαιτείται τεχνητή προσθήκη P2 item σε αυτό το baseline. |

| Applicability | Ερμηνεία |
|---|---|
| D | Ελεγχόμενη ακαδημαϊκή επίδειξη με synthetic data. |
| F | Ολοκλήρωση της σχετικής λειτουργίας. Οι μελλοντικοί έλεγχοι δεν επιβάλλουν δημιουργία feature εκτός scope. |
| R | Μελλοντική πραγματική χρήση / δημόσια παραγωγή, που παραμένει μη εξουσιοδοτημένη σήμερα. |

Πολλαπλές ενδείξεις δηλώνουν περισσότερα του ενός contexts. Το D δεν σημαίνει ότι κάθε production κενό πρέπει να υλοποιηθεί πριν από απομονωμένο synthetic demo. Τα demo safeguards και οι εξαιρέσεις ορίζονται στην ενότητα 8. Τα P0 δεν υποβαθμίζονται για future production και τα P1 απαιτούνται για κάθε released feature. Αριθμητικά όρια, RPO/RTO και deadlines δεν επινοούνται· χρειάζονται εγκεκριμένες τιμές.

## 4. Evidence catalogue και verification conventions

### 4.1 Υλοποίηση και configuration

Τα E IDs αντιστοιχούν στο SECURITY-REQUIREMENTS.md. Τα σχετικά αρχεία είναι evidence locations, όχι δήλωση ότι κάθε control στο οποίο παραπέμπουν είναι ολοκληρωμένο.

| Evidence | Αρχεία |
|---|---|
| E01 | [Authentication routes](../../backend/app/api/auth.py), [User schemas](../../backend/app/schemas/user.py), [User model](../../backend/app/db/models/user.py) |
| E02 | [Security utilities](../../backend/app/core/security.py), [Settings](../../backend/app/core/config.py) |
| E03 | [Identity/clinic dependencies](../../backend/app/api/deps.py), [Permission policy](../../backend/app/core/permissions.py) |
| E04 | [Clinic](../../backend/app/db/models/clinic.py), [ClinicMembership](../../backend/app/db/models/clinic_membership.py), [MembershipRole](../../backend/app/db/models/membership_role.py) |
| E05 | [Application routes](../../backend/app/main.py), [DB session](../../backend/app/db/session.py) |
| E06 | [AuthProvider](../../frontend/src/auth/AuthProvider.tsx), [ProtectedRoute](../../frontend/src/auth/ProtectedRoute.tsx), [App](../../frontend/src/App.tsx) |
| E07 | [API client](../../frontend/src/api/client.ts), [Auth client](../../frontend/src/api/auth.ts), [LoginPage](../../frontend/src/pages/LoginPage.tsx) |
| E08 | [Compose](../../docker-compose.yml), [Backend Dockerfile](../../backend/Dockerfile), [Frontend Dockerfile](../../frontend/Dockerfile), [Vite config](../../frontend/vite.config.ts) |
| E09 | [.env.example](../../.env.example), [.gitignore](../../.gitignore), [Alembic environment](../../backend/alembic/env.py), [Alembic config](../../backend/alembic.ini) |
| E10 | [User migration](../../backend/alembic/versions/71eda1fd3061_create_users_table.py), [Clinic/membership migration](../../backend/alembic/versions/a807f733a8e3_create_clinic_membership_tables.py) |
| E11 | [Backend requirements](../../backend/requirements.txt), [Test requirements](../../backend/requirements-test.txt), [Frontend manifest](../../frontend/package.json), [Frontend lockfile](../../frontend/package-lock.json) |
| E12 | [Test bootstrap](../../backend/tests/conftest.py), [Test Compose](../../docker-compose.test.yml), [Frontend test runner](../../frontend/tests/run-api-tests.mjs) |

### 4.2 Υπάρχοντα tests ως πηγαίος κώδικας

| ID | Test source / δηλωμένο εύρος |
|---|---|
| T01 | [test_auth.py](../../backend/tests/test_auth.py): JWT claims/signature/expiry, successful login με mocked password verification. |
| T02 | [test_current_user.py](../../backend/tests/test_current_user.py): identity, inactive/nonexistent User, invalid credentials και DB failure propagation. |
| T03 | [test_auth_me.py](../../backend/tests/test_auth_me.py): protected endpoint και filtered User response. |
| T04 | [test_clinic_context.py](../../backend/tests/test_clinic_context.py): membership/context isolation μέσω test-only route. |
| T05 | [test_permissions.py](../../backend/tests/test_permissions.py): exact permission matrix, role union και empty roles. |
| T06 | [test_clinic_authorization.py](../../backend/tests/test_clinic_authorization.py): test-only request matrix, cross-clinic roles, no bypass και same-JWT changes. |
| T07 | [test_clinic_membership_constraints.py](../../backend/tests/test_clinic_membership_constraints.py): foundation FK/unique/enum constraints. |
| T08 | [auth-provider.test.tsx](../../frontend/tests/auth-provider.test.tsx): memory state, login→me, logout και stale responses. |
| T09 | [api.test.mjs](../../frontend/tests/api.test.mjs): request encoding, bearer header και error classification/messages. |
| T10 | [login-page.test.tsx](../../frontend/tests/login-page.test.tsx): safe UI errors, password clearing και limited DOM leakage checks. |
| T11 | [routing.test.tsx](../../frontend/tests/routing.test.tsx): UI routing και memory-only state μετά remount. |

Η εκτέλεση των παραπάνω δεν έγινε σε αυτή την εργασία. Το E12 database fixture εκτελεί Alembic upgrade όταν ζητηθεί, περιορίζει το test DB target και χρησιμοποιεί rollback. Δεν αποδεικνύει successful migration εδώ, production backup ή tenant isolation όλων των resources.

### 4.3 Εγκεκριμένες αποφάσεις και evidence limits

- OWNER έχει όλες τις δηλωμένες permissions μέσα στη δική του Clinic, μαζί με medical-record permissions. Δεν έχει cross-clinic bypass.
- Roles συνδυάζονται μόνο στην ίδια Clinic. Το `is_superuser` δεν παρακάμπτει membership/permission checks.
- Clinic/RBAC είναι implemented foundations μέσω test-only routes. Patient domain endpoints και tenant-scoped Patient operations δεν έχουν υλοποιηθεί.
- OWNER δεν είναι αυτόματα Doctor profile. Acting User και responsible Doctor θα καταγράφονται χωριστά· exact schema/attribution pending.
- OTP, audit logging, rate limiting, production TLS, backup recovery και production hardening δεν τεκμηριώνονται ως ολοκληρωμένα.
- Τα πραγματικά auth routes είναι `/auth/*`: το configured `API_PREFIX` δεν εφαρμόζεται στο router inclusion.
- Documentation αποδεικνύει απαίτηση ή απόφαση, όχι runtime enforcement. Error propagation tests δεν αποδεικνύουν log sanitization. Persistent volume δεν αποδεικνύει backup.
- Νέο verification γίνεται σε ασφαλές περιβάλλον με approved scope, χωρίς καταγραφή secrets. Αρνητικό security test θεωρείται επιτυχές όταν η μη εξουσιοδοτημένη πράξη απορρίπτεται χωρίς leakage ή mutation.

## 5. Checklist: 48 stable checks σε 15 ομάδες

Κάθε επικεφαλίδα είναι η συγκεκριμένη ερώτηση Ναι/Όχι. Η ένδειξη Implemented αφορά μόνο το περιορισμένο εύρος της ερώτησης. Όλα τα verification results παραμένουν Not verified μέχρι ξεχωριστή εκτέλεση release verification.

### 5.1 Authentication και staff account lifecycle

#### CHK-001 — Γίνεται hashing των passwords πριν από την αποθήκευσή τους κατά το registration;

- **Priority:** P0
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E01/E02: το register_user καλεί get_password_hash πριν δημιουργήσει User. Το T01 κάνει mock το password verification στο successful-login test.
- **SEC references:** SEC-002
- **TM references:** TM-001
- **Verification method:** Review του persistence path και πραγματικά hash/verify tests, με έλεγχο ότι δεν αποθηκεύεται plaintext.
- **Release applicability:** D/F/R

#### CHK-002 — Απορρίπτονται οι inactive users τόσο κατά την έκδοση token όσο και κατά την πρόσβαση σε protected endpoints;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E01/E03 και T02/T03: το protected dependency αρνείται inactive User, αλλά το login δεν ελέγχει activation πριν εκδώσει token.
- **SEC references:** SEC-003
- **TM references:** TM-001, TM-002
- **Verification method:** Inactive login και requests με ήδη εκδομένο token μετά deactivation· έλεγχος ότι δεν εκδίδεται νέο token και δεν επιτρέπεται protected operation.
- **Release applicability:** D/F/R

#### CHK-003 — Ακολουθεί η δημιουργία staff το εξουσιοδοτημένο OWNER bootstrap/invitation flow χωρίς μη εξουσιοδοτημένη ανάθεση roles;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** E01: υπάρχει public registration χωρίς membership assignment. Δεν υπάρχει bootstrap/invitation implementation ή σχετική test evidence.
- **SEC references:** SEC-001, SEC-011
- **TM references:** TM-007
- **Verification method:** Tests για bootstrap authority, unauthorized target/Clinic/role, invitation expiry και replay. Δεν θεωρείται το public registration απόδειξη clinic-access bypass.
- **Release applicability:** F/R

#### CHK-004 — Υπάρχει εγκεκριμένη και ασφαλώς επαληθευμένη διαδικασία recovery και αλλαγής credentials;

- **Priority:** P1
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Δεν βρέθηκαν recovery/change endpoints ή approved operational διαδικασία. Η αναφορά SEC-005 δεν αποτελεί implementation evidence.
- **SEC references:** SEC-005, SEC-007
- **TM references:** TM-001, TM-002
- **Verification method:** Review εγκεκριμένου workflow, single-use recovery και session invalidation evidence· ή τεκμηριωμένος αποκλεισμός της λειτουργίας με ασφαλή εναλλακτική.
- **Release applicability:** F/R

### 5.2 JWT και session security

#### CHK-005 — Απορρίπτει ο validator invalid signatures, missing required claims, expired tokens και invalid user subjects;

- **Priority:** P1
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E02/T01: απαιτούμενα sub/exp, signature/expiry και positive PostgreSQL Integer subject validation. Πρόκειται για βασικό validator, όχι πλήρες token contract.
- **SEC references:** SEC-006
- **TM references:** TM-002, TM-003
- **Verification method:** Εκτέλεση των σχετικών αρνητικών JWT tests για το συγκεκριμένο release και καταγραφή αποτελεσμάτων.
- **Release applicability:** D/F/R

#### CHK-006 — Έχει οριστεί και επιβάλλεται πλήρες token validation contract, μαζί με permitted algorithms και token purpose;

- **Priority:** P1
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E02: configured algorithm και βασικά claims. Purpose/issuer/audience αποφάσεις και πλήρης verification παραμένουν ανοικτά.
- **SEC references:** SEC-006, SEC-014
- **TM references:** TM-003, TM-018
- **Verification method:** Review του εγκεκριμένου contract και tests απόρριψης για κάθε κανόνα, ιδίως λάθος algorithm ή identity purpose.
- **Release applicability:** F/R

#### CHK-007 — Εφαρμόζουν expiration, logout και credential changes την εγκεκριμένη session/replay policy;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E02/E06: JWT expiry και local logout. Δεν υπάρχει server revocation ή credential-change invalidation evidence.
- **SEC references:** SEC-007, SEC-008
- **TM references:** TM-002
- **Verification method:** Copied-token replay πριν/μετά logout, expiration, deactivation και credential changes έναντι της εγκεκριμένης πολιτικής.
- **Release applicability:** D/F/R

### 5.3 Clinic membership και RBAC

#### CHK-008 — Απαιτεί η επίλυση Clinic context membership του τρέχοντος χρήστη στην αιτούμενη Clinic;

- **Priority:** P1
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E03/T04: query με user_id και clinic_id, validated path και ισοδύναμα inaccessible/nonexistent responses. Foundation μέσω test-only routes.
- **SEC references:** SEC-010
- **TM references:** TM-005, TM-006
- **Verification method:** Context/invalid-ID/membership-change tests, συμπεριλαμβανομένου ίδιου JWT μετά αλλαγή membership και no-superuser-bypass.
- **Release applicability:** D/F/R

#### CHK-009 — Δίνει το RBAC στον OWNER όλες τις δηλωμένες permissions μόνο εντός της δικής του Clinic και συνδυάζει roles μόνο μέσα στην ίδια Clinic;

- **Priority:** P0
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E03/T05/T06: exact matrix, clinic-local union, empty roles και no-superuser-bypass assertions. Η ένδειξη αφορά foundation, όχι domain endpoint integration.
- **SEC references:** SEC-011, SEC-013
- **TM references:** TM-006, TM-008
- **Verification method:** Exact policy tests με OWNER-only, πολλαπλά roles στην ίδια Clinic και διαφορετικά roles σε άλλες Clinics· αρνητικά cross-clinic tests.
- **Release applicability:** D/F/R

#### CHK-010 — Καλεί κάθε domain endpoint που διατίθεται τους απαιτούμενους authentication, membership και permission ελέγχους;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Υπάρχουν E03 dependencies και T04/T06 test-only routes. Δεν υπάρχουν Patient/domain endpoints στο baseline.
- **SEC references:** SEC-009, SEC-010, SEC-011, SEC-012, SEC-013
- **TM references:** TM-005, TM-006, TM-007, TM-008
- **Verification method:** Endpoint inventory και απευθείας HTTP negative tests για missing/invalid identity, membership και operation permission.
- **Release applicability:** F/R

### 5.4 Tenant isolation και IDOR prevention

#### CHK-011 — Περιορίζονται resource reads και mutations ταυτόχρονα από authorized Clinic και resource ID;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχουν Patient/resource queries ή domain-resource isolation tests. E03 περιορίζει membership, όχι αυθαίρετα ORM resources.
- **SEC references:** SEC-012
- **TM references:** TM-005
- **Verification method:** Two-clinic read/update/delete και parent/child ID substitution tests σε πραγματικά released endpoints· επιβεβαίωση ότι denied requests δεν μεταβάλλουν δεδομένα.
- **Release applicability:** F/R

#### CHK-012 — Ορίζεται το resource ownership από trusted context και απορρίπτονται conflicting tenant inputs και unauthorized reparenting;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχουν domain create/update services. Η αρχιτεκτονική §9 περιγράφει στόχο, όχι εφαρμοσμένο control.
- **SEC references:** SEC-012, SEC-017
- **TM references:** TM-005, TM-009
- **Verification method:** Forged clinic_id, mass assignment και reparenting requests· έλεγχος persisted ownership και απόρριψης μη εξουσιοδοτημένης αλλαγής.
- **Release applicability:** F/R

#### CHK-013 — Περιορίζονται ανά tenant lists, searches, counts, pagination metadata και όσα exports/analytics έχουν διατεθεί;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει domain retrieval/aggregation implementation. Patient counts και lists δεν καλύπτονται από foundation tests.
- **SEC references:** SEC-012, SEC-019
- **TM references:** TM-005, TM-013
- **Verification method:** Mixed-clinic fixtures με assertions για περιεχόμενο, totals και τυχόν released export/analytics output. Δεν απαιτείται δημιουργία νέων features για να εκτελεστεί το check.
- **Release applicability:** F/R

#### CHK-014 — Ελέγχονται οι linked resources για same-clinic ownership, με database constraints όπου είναι πρακτικό;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** E04/E10 περιέχουν μόνο foundation membership/role constraints. Domain relationships και οι αντίστοιχοι έλεγχοι δεν υπάρχουν.
- **SEC references:** SEC-012, SEC-018
- **TM references:** TM-009
- **Verification method:** Linked-ID substitutions, απευθείας constraint failures όπου υπάρχουν constraints και rollback χωρίς partial mutations.
- **Release applicability:** F/R

### 5.5 Patients και Medical Records

#### CHK-015 — Εκθέτουν τα Patient schemas μόνο επιτρεπόμενα administrative fields χωρίς περιττή αποκάλυψη AMKA ή clinical content;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Patient schemas/APIs απουσιάζουν. Το υφιστάμενο UserOut δεν αποδεικνύει Patient field protection.
- **SEC references:** SEC-013, SEC-019, SEC-030
- **TM references:** TM-008, TM-013
- **Verification method:** Response-field assertions για Patient lists/details, συμπεριλαμβανομένου approved AMKA use και absence of clinical fields για administrative callers.
- **Release applicability:** F/R

#### CHK-016 — Επιβάλλουν τα clinical endpoints την εγκεκριμένη OWNER/DOCTOR/SECRETARY policy μέσα στα Clinic boundaries;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E03/T05/T06: permission policy υπάρχει. Clinical endpoints και field-level enforcement δεν έχουν υλοποιηθεί.
- **SEC references:** SEC-011, SEC-013
- **TM references:** TM-006, TM-008
- **Verification method:** OWNER χωρίς DOCTOR επιτρέπεται τοπικά· SECRETARY χωρίς κατάλληλο πρόσθετο role απορρίπτεται· όλοι απορρίπτονται εκτός εξουσιοδοτημένης Clinic.
- **Release applicability:** F/R

#### CHK-017 — Καταγράφουν τα clinical workflows acting User χωριστά από responsible Doctor, χωρίς αυτόματη μετατροπή OWNER σε Doctor;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Πρόκειται για εγκεκριμένη architecture απόφαση. Δεν υπάρχει clinical schema/workflow implementation. Ακριβείς attribution rules παραμένουν pending.
- **SEC references:** SEC-013, SEC-018, SEC-021
- **TM references:** TM-009, TM-010
- **Verification method:** Review approved schema/attribution rules και tests για server-derived actor, ανεξάρτητο responsible Doctor και OWNER-only workflow χωρίς πλαστή Doctor identity.
- **Release applicability:** F/R

### 5.6 Appointments, Payments και relationship integrity

#### CHK-018 — Ελέγχουν τα Appointments same-clinic Patient/doctor relationships και αποτρέπουν prohibited concurrent overlaps;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχουν Appointment model/service ή concurrency tests στο baseline.
- **SEC references:** SEC-012, SEC-017, SEC-018
- **TM references:** TM-009, TM-015
- **Verification method:** Relationship substitutions, εγκεκριμένα state/eligibility cases και controlled concurrent booking tests σε απομονωμένο περιβάλλον.
- **Release applicability:** F/R

#### CHK-019 — Ανήκει το optional Appointment ενός Payment στον επιλεγμένο Patient και στην ίδια Clinic;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Payment implementation απουσιάζει. Same-clinic ownership μόνο του δεν αποδεικνύει same-Patient consistency.
- **SEC references:** SEC-012, SEC-018
- **TM references:** TM-009
- **Verification method:** Same-clinic/wrong-Patient και cross-clinic combinations, μαζί με database enforcement όπου πρακτικό.
- **Release applicability:** F/R

#### CHK-020 — Αναιρούνται οι αποτυχημένες domain operations χωρίς partial writes ή παραπλανητικά successful audit events;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχουν domain transaction/audit services. Το test transaction rollback του E12 δεν αποτελεί εφαρμοσμένη domain transaction policy.
- **SEC references:** SEC-018, SEC-021
- **TM references:** TM-009, TM-010
- **Verification method:** Controlled failure injection, έλεγχος τελικής DB/audit κατάστασης και επιβεβαίωση ότι action που έγινε rollback δεν καταγράφεται ως επιτυχές.
- **Release applicability:** F/R

### 5.7 Patient Portal, AMKA και OTP

#### CHK-021 — Παραμένουν τα patient principals/sessions χωριστά από staff identity και περιορισμένα σε authorized appointment operations;

- **Priority:** P1
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει Portal/session implementation. Η απαίτηση διαχωρισμού στην προδιαγραφή δεν είναι runtime control.
- **SEC references:** SEC-014, SEC-016
- **TM references:** TM-018
- **Verification method:** Patient-to-staff rejection, cross-patient/Clinic denial, appointment eligibility και αποκλεισμός medical records.
- **Release applicability:** F/R

#### CHK-022 — Δεσμεύονται τα OTPs σε verified destinations, υπόκεινται σε approved limits και εξαργυρώνονται atomic single-use;

- **Priority:** P1
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει OTP/provider/challenge implementation ή σχετική test evidence.
- **SEC references:** SEC-015, SEC-020
- **TM references:** TM-018
- **Verification method:** Expiry, guessing/attempt limits, resend behavior, replay, concurrent redemption και wrong destination/identity cases έναντι εγκεκριμένων policies.
- **Release applicability:** F/R

#### CHK-023 — Αποφεύγει το public AMKA verification την αποκάλυψη ύπαρξης Patient ή σχέσης του με Clinic;

- **Priority:** P1
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** AMKA/Portal endpoints απουσιάζουν. Δεν έχει εκτελεστεί enumeration ή timing verification.
- **SEC references:** SEC-016, SEC-019
- **TM references:** TM-012, TM-013
- **Verification method:** Known/unknown identifiers, public response semantics, approved timing assessment και επιθεώρηση URLs/logs για sensitive identifiers.
- **Release applicability:** F/R

### 5.8 Input validation, responses και errors

#### CHK-024 — Είναι όλα τα inputs των διαθέσιμων λειτουργιών bounded και validated server-side βάσει εγκεκριμένων field/resource rules;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E01/E03: email/schema types και clinic path bounds. Πλήρη password/body/domain limits δεν υπάρχουν.
- **SEC references:** SEC-002, SEC-017
- **TM references:** TM-001, TM-009, TM-015
- **Verification method:** Boundary, malformed και oversized requests, συμπεριλαμβανομένων password UTF-8 byte boundaries και pagination όπου υπάρχει.
- **Release applicability:** D/F/R

#### CHK-025 — Αποκλείουν explicit response schemas hashes, secrets και μη εξουσιοδοτημένα sensitive fields;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E01/T03: UserOut excludes password hash. Domain response schemas απουσιάζουν.
- **SEC references:** SEC-019
- **TM references:** TM-008, TM-013
- **Verification method:** Schema review και raw-response assertions για όσα endpoints διατίθενται, όχι μόνο έλεγχος rendered UI.
- **Release applicability:** D/F/R

#### CHK-026 — Επιστρέφονται validation, database και concurrent-request failures χωρίς sensitive technical details;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E07/T09/T10: safe UI messages. Πλήρης backend sanitization και log protection δεν έχουν επαληθευθεί.
- **SEC references:** SEC-004, SEC-019, SEC-022
- **TM references:** TM-012, TM-013
- **Verification method:** Controlled failures, response assertions και captured logs χωρίς SQL/credentials/stack traces/clinical payloads. Error propagation tests δεν αρκούν.
- **Release applicability:** D/F/R

### 5.9 Rate limiting και abuse prevention

#### CHK-027 — Επιβάλλουν τα διαθέσιμα authentication/registration/recovery/OTP endpoints εγκεκριμένα abuse limits;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν βρέθηκε limiter implementation. Η απουσία recovery/OTP endpoint δεν μετατρέπει όλο το baseline control σε Not Applicable.
- **SEC references:** SEC-020
- **TM references:** TM-001, TM-012, TM-015, TM-018
- **Verification method:** Account/IP/challenge limits και concurrent requests με approved thresholds, χωρίς ανεξέλεγκτο account-lockout abuse.
- **Release applicability:** F/R

#### CHK-028 — Επιβάλλουν τα expensive APIs request/result limits κατάλληλα για το deployment;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχουν ολοκληρωμένα body/query/quota controls ή capacity verification evidence.
- **SEC references:** SEC-017, SEC-020
- **TM references:** TM-015
- **Verification method:** Approved request/result boundaries και controlled resource-consumption tests σε απομονωμένο περιβάλλον, μόνο για διαθέσιμα APIs.
- **Release applicability:** F/R

#### CHK-029 — Έχουν επαληθευθεί client-IP/proxy trust και multi-instance limit behavior για το επιλεγμένο deployment;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Η πραγματική deployment topology, trusted proxies και enforcement δεν έχουν επαληθευθεί.
- **SEC references:** SEC-020, SEC-024, SEC-026
- **TM references:** TM-004, TM-015
- **Verification method:** Trusted/untrusted forwarding headers και κοινό limit enforcement αν χρησιμοποιούνται πολλά instances· τεκμηρίωση της selected topology.
- **Release applicability:** R

### 5.10 Audit logging και privacy

#### CHK-030 — Αποδίδονται τα εγκεκριμένα security/clinical events σε actor και προστατεύεται το audit από μη εξουσιοδοτημένη αλλοίωση;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει application audit implementation. Creation timestamps και default server logs δεν επαρκούν.
- **SEC references:** SEC-021
- **TM references:** TM-007, TM-010, TM-011
- **Verification method:** Actor/Clinic/action/target/time/outcome event tests, denied-attempt policy, access restrictions και update/delete/tampering tests.
- **Release applicability:** F/R

#### CHK-031 — Αποκλείουν application/access/error logs credentials, tokens, OTPs, πλήρη AMKA και clinical content;

- **Priority:** P0
- **Implementation status:** Planned
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει systematic redaction ή captured-log evidence. Απουσία explicit logging δεν αποδεικνύει ασφαλή defaults.
- **SEC references:** SEC-022
- **TM references:** TM-011, TM-013
- **Verification method:** Captured logs για success, validation, DB και provider failures όπου εφαρμόζονται· έλεγχος exception parameters και request-body leakage.
- **Release applicability:** D/F/R

#### CHK-032 — Έχουν εγκριθεί purposes, retention, access/export/deletion και privacy responsibilities για την προβλεπόμενη χρήση;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Υπάρχει synthetic-only απόφαση. Operational real-data policy και qualified governance assessment δεν έχουν τεκμηριωθεί.
- **SEC references:** SEC-030, SEC-031
- **TM references:** TM-010, TM-013, TM-016
- **Verification method:** Data inventory, αρμόδιες ευθύνες και approved procedures για πραγματική χρήση· χωρίς αυτόματο συμπέρασμα GDPR compliance.
- **Release applicability:** R

### 5.11 Secrets και dependency management

#### CHK-033 — Παρέχονται τα secrets εξωτερικά, αποκλείονται από artifacts και απορρίπτονται όταν λείπουν ή είναι unsafe για το target environment;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E02/E09: environment settings, required key και βασικά ignore rules. Production validation/artifact exclusion δεν είναι ολοκληρωμένα.
- **SEC references:** SEC-023
- **TM references:** TM-003, TM-017
- **Verification method:** Settings failure cases και repository/image/bundle review χωρίς εκτύπωση μυστικών· έλεγχος placeholder/development defaults.
- **Release applicability:** D/F/R

#### CHK-034 — Έχουν οριστεί και μπορούν να επαληθευθούν secret access, rotation και compromise procedures;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει operational custody/rotation evidence. Minimum key length δεν αποδεικνύει entropy ή ασφαλή custody.
- **SEC references:** SEC-023, SEC-029
- **TM references:** TM-003, TM-016
- **Verification method:** Access review και controlled rotation exercise με εγκεκριμένη συμπεριφορά για παλιά tokens/credentials.
- **Release applicability:** R

#### CHK-035 — Καταγράφονται dependency/image resolution και vulnerability-review results για το release;

- **Priority:** P1
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E11: manifests, frontend lockfile και ορισμένα version constraints. Backend κυρίως unpinned· δεν υπάρχει scan-run evidence.
- **SEC references:** SEC-027
- **TM references:** TM-014, TM-017
- **Verification method:** Reproducibility/build review και documented scan/remediation results. Δεν δηλώνεται συγκεκριμένη dependency ως ευάλωτη χωρίς evidence.
- **Release applicability:** D/F/R

### 5.12 Frontend/browser security

#### CHK-036 — Διατηρεί το σημερινό frontend authentication στη μνήμη και το καθαρίζει σε logout/remount χωρίς late-response restoration;

- **Priority:** P1
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E06/T08/T11: memory-only state και stale-response handling. Δεν περιγράφεται server-side revocation.
- **SEC references:** SEC-008
- **TM references:** TM-002, TM-014
- **Verification method:** Provider/routing tests, storage inspection και pending-login/logout/remount scenarios για το συγκεκριμένο release.
- **Release applicability:** D/F/R

#### CHK-037 — Περιμένει το σημερινό UI το /auth/me και αποτρέπει unauthenticated dashboard navigation;

- **Priority:** P1
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E06/T08/T11: login→me και ProtectedRoute. Πρόκειται για UI flow μόνο.
- **SEC references:** SEC-008, SEC-009
- **TM references:** TM-002, TM-008
- **Verification method:** Login/current-user failures και direct navigation tests· οι backend authorization έλεγχοι επαληθεύονται ανεξάρτητα.
- **Release applicability:** D/F/R

#### CHK-038 — Έχουν επαληθευθεί production browser/origin/header controls για τον επιλεγμένο authentication μηχανισμό;

- **Priority:** P1
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει verified production CSP/header/origin policy ή deployment evidence.
- **SEC references:** SEC-025
- **TM references:** TM-004, TM-014
- **Verification method:** Deployed header/origin checks και unsafe-rendering tests· cookie/CSRF verification μόνο εφόσον εισαχθούν cookies.
- **Release applicability:** R

### 5.13 Database, Docker και deployment security

#### CHK-039 — Επιβάλλουν τα foundation membership/role tables τους foreign-key, uniqueness και enum κανόνες τους;

- **Priority:** P0
- **Implementation status:** Implemented
- **Verification result:** Not verified
- **Evidence:** E04/E10/T07: model/migration constraints και αντίστοιχα test assertions. Δεν περιλαμβάνει domain relationships.
- **SEC references:** SEC-018
- **TM references:** TM-007, TM-009
- **Verification method:** Relevant PostgreSQL constraint tests στο ασφαλές test environment και review migration definitions· χωρίς υπόθεση domain integrity.
- **Release applicability:** D/F/R

#### CHK-040 — Περιορίζονται runtime DB privileges και database/admin network exposure;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** E08 δημοσιεύει DB port στον host. Live reachability, runtime privileges και administrative access δεν έχουν ελεγχθεί.
- **SEC references:** SEC-018, SEC-026
- **TM references:** TM-016
- **Verification method:** Network exposure review και έλεγχος runtime έναντι migration/admin roles για το πραγματικό περιβάλλον.
- **Release applicability:** D/R

#### CHK-041 — Αποφεύγει το production deployment development servers/mounts και χρησιμοποιεί hardened, reviewed images;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** E08: containers υπάρχουν, αλλά χρησιμοποιούν reload/Vite, bind mounts και δεν δηλώνουν non-root user. Production hardening δεν τεκμηριώνεται.
- **SEC references:** SEC-009, SEC-026, SEC-027
- **TM references:** TM-015, TM-016, TM-017
- **Verification method:** Production build/configuration review, ports/mounts/users, image contents και εγκεκριμένο public endpoint inventory.
- **Release applicability:** R

#### CHK-042 — Προστατεύεται η απαιτούμενη επικοινωνία από verified TLS και approved proxy/network configuration;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Development HTTP υπάρχει· production transport και εξωτερική υποδομή δεν έχουν επαληθευθεί.
- **SEC references:** SEC-024, SEC-026
- **TM references:** TM-004
- **Verification method:** Deployment TLS/certificate/HTTP behavior, trusted proxy configuration και σχετικά internal links σύμφωνα με το threat model.
- **Release applicability:** R

### 5.14 Backups, recovery και incident handling

#### CHK-043 — Υπάρχουν backups των αναγκαίων δεδομένων με εγκεκριμένα access, encryption, retention και key custody;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** E08: persistent volume μόνο· απουσιάζουν backup configuration/run evidence και encryption/custody verification.
- **SEC references:** SEC-028
- **TM references:** TM-016
- **Verification method:** Backup inventory/configuration review για foundation και released domain data, μαζί με προστασία keys και περιορισμένη πρόσβαση.
- **Release applicability:** R

#### CHK-044 — Έχει αποδείξει isolated restore integrity, tenant separation και τα εγκεκριμένα recovery objectives;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Δεν υπάρχει restore-run evidence. Test DB setup/rollback δεν αποτελεί production recovery.
- **SEC references:** SEC-028
- **TM references:** TM-016
- **Verification method:** Καταγεγραμμένο isolated restore exercise με integrity/tenant/application checks έναντι approved RPO/RTO.
- **Release applicability:** R

#### CHK-045 — Έχουν ασκηθεί incident ownership, containment, evidence preservation, rotation και recovery procedures;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Δεν βρέθηκαν incident-runbook/tabletop execution evidence.
- **SEC references:** SEC-029
- **TM references:** TM-003, TM-010, TM-011, TM-016
- **Verification method:** Review approved runbook και tabletop με καταγεγραμμένα αποτελέσματα, responsibilities και corrective actions.
- **Release applicability:** R

### 5.15 Automated tests και release gates

#### CHK-046 — Έχουν ελεγχθεί το πραγματικό demo dataset και το περιβάλλον για synthetic-only περιεχόμενο και controlled exposure;

- **Priority:** P0
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** Η πολιτική είναι εγκεκριμένη, αλλά δεν επαληθεύθηκε συγκεκριμένο dataset/deployment κατά την επιθεώρηση ή τη σύνταξη.
- **SEC references:** SEC-030, SEC-031, SEC-032
- **TM references:** TM-004, TM-013, TM-016
- **Verification method:** Seed/data/screenshots/exports/logs review, πραγματική port reachability και επιβεβαίωση ότι credentials/host παραμένουν προστατευμένα.
- **Release applicability:** D

#### CHK-047 — Έχουν καταγραφεί relevant test results για το ακριβές release commit και περιβάλλον;

- **Priority:** P1
- **Implementation status:** Unknown
- **Verification result:** Not verified
- **Evidence:** T01–T11 υπάρχουν ως test source. Δεν εκτελέστηκαν tests στο SECURITY-00D και δεν πιστοποιείται άλλο release run.
- **SEC references:** SEC-032
- **TM references:** TM-001, TM-002, TM-003, TM-004, TM-005, TM-006, TM-007, TM-008, TM-009, TM-010, TM-011, TM-012, TM-013, TM-014, TM-015, TM-016, TM-017, TM-018
- **Verification method:** Πραγματικά commands/results με failures/skips, commit/environment και test DB safeguards. Αποθήκευση ασφαλών evidence χωρίς secrets.
- **Release applicability:** D/F/R

#### CHK-048 — Έχει εγκριθεί το release έναντι των applicable checks, με καταγεγραμμένα unresolved blockers και exceptions;

- **Priority:** P0
- **Implementation status:** Partial
- **Verification result:** Not verified
- **Evidence:** Demo/production gates είναι documented. Operational execution/sign-off δεν έχει επαληθευθεί· production authorization δεν υπάρχει.
- **SEC references:** SEC-030, SEC-031, SEC-032
- **TM references:** TM-001, TM-002, TM-003, TM-004, TM-005, TM-006, TM-007, TM-008, TM-009, TM-010, TM-011, TM-012, TM-013, TM-014, TM-015, TM-016, TM-017, TM-018
- **Verification method:** Completed release review record, reviewer/exceptions και νέα ρητή έγκριση πριν από οποιαδήποτε future real-data production χρήση.
- **Release applicability:** D/F/R

## 6. BACKEND-02C — Patients & Tenant Isolation acceptance subset

Το subset αφορά μόνο Patient endpoints και λειτουργίες που περιλαμβάνονται ρητά στο BACKEND-02C. Δεν εισάγει Medical Records, Portal, exports, analytics ή production infrastructure στο scope. Ελέγχει όμως ότι οι Patient responses δεν εκθέτουν μη επιτρεπόμενα clinical fields. Αν κάποια προαιρετική operation δεν διατίθεται, καταγράφεται ως release-scope exclusion, όχι ως ολοκληρωμένο control.

| Απαίτηση αποδοχής για BACKEND-02C | CHK links |
|---|---|
| Κάθε Patient endpoint απαιτεί current active staff identity, membership και exact operation permission. | CHK-008, CHK-009, CHK-010 |
| Reads και writes περιορίζονται από authorized Clinic μαζί με Patient ID. Denied mutations δεν αλλάζουν δεδομένα. | CHK-011 |
| Create ownership προέρχεται από trusted context· conflicting ownership, mass assignment και unauthorized reparenting απορρίπτονται. | CHK-012 |
| Patient lists, searches όπου υπάρχουν, counts και pagination metadata δεν διαρρέουν άλλη Clinic. | CHK-013 |
| Κάθε linked resource μέσα στο συγκεκριμένο scope ανήκει στην ίδια Clinic. Δεν απαιτείται δημιουργία μελλοντικών relationships. | CHK-014 |
| Responses περιλαμβάνουν μόνο approved administrative fields και αποφεύγουν περιττή AMKA/clinical αποκάλυψη. | CHK-015, CHK-025 |
| Validation/database failures έχουν controlled responses χωρίς sensitive technical details. | CHK-024, CHK-026 |
| Patient ownership/constraints έχουν reviewed Alembic migration και domain transactions δεν αφήνουν partial writes. | CHK-020, CHK-039 |
| Πραγματικά Patient endpoint negative tests εκτελούνται και καταγράφονται πριν feature completion. Test-only RBAC routes δεν επαρκούν. | CHK-047, CHK-048 |

Το CHK-039 καλύπτει σημερινά foundation constraints. Για το νέο Patient schema απαιτείται πρόσθετο συγκεκριμένο migration/constraint evidence· δεν κληρονομείται αυτόματα το Implemented status.

Δεν επινοούνται AMKA uniqueness, global Patient identity, deletion/retention ή hard-delete rules. Αυτά χρειάζονται domain απόφαση πριν σχετικό implementation. Το `patients.delete` permission δεν καθορίζει μόνο του deletion policy. Audit/logging gaps που δεν περιλαμβάνονται στην Patient εργασία καταγράφονται ως production εκκρεμότητες, χωρίς να παρουσιάζονται ως υλοποιημένα ή να επεκτείνεται σιωπηρά η εργασία.

## 7. Patient negative-test matrix

Όλες οι παρακάτω γραμμές είναι **προτεινόμενο verification**, όχι εκτελεσμένα tests. Χρησιμοποιούνται συνθετικοί Users/Patients σε τουλάχιστον δύο διακριτές Clinics και πραγματικά Patient endpoints. Για κάθε denied mutation ελέγχεται και η αμετάβλητη DB κατάσταση.

| Case | Αναμενόμενο αποτέλεσμα | CHK / SEC / TM |
|---|---|---|
| Missing, malformed ή expired bearer token | Απόρριψη προστατευμένης πρόσβασης χωρίς Patient data/mutation. | CHK-005, CHK-010 / SEC-006, SEC-009 / TM-002 |
| Ανύπαρκτος ή inactive User με token | Απόρριψη μέσω current-user validation. Το inactive-login gap ελέγχεται χωριστά και δεν εξουσιοδοτεί Patient πρόσβαση. | CHK-002, CHK-010 / SEC-003, SEC-009 / TM-001, TM-002 |
| User χωρίς membership στην αιτούμενη Clinic | Κανένα Patient access· consistent inaccessible/nonexistent Clinic behavior. | CHK-008, CHK-010 / SEC-010 / TM-005, TM-006 |
| Membership χωρίς roles | Καμία operation permission, ακόμη αν το context επιλύεται. | CHK-009, CHK-010 / SEC-011 / TM-006 |
| OWNER στην A ζητά Patient της B | Απόρριψη χωρίς OWNER ή superuser bypass. | CHK-009, CHK-011 / SEC-011, SEC-012 / TM-005, TM-006 |
| OWNER στην A και SECRETARY στην B | Στην B ισχύουν μόνο οι permissions της εκεί membership· κανένα OWNER-only privilege από την A. | CHK-009, CHK-010 / SEC-011 / TM-006 |
| Πολλαπλά roles μέσα στην ίδια Clinic | Επιτρέπεται ακριβώς η ένωση του approved matrix, χωρίς επιπλέον OWNER-only permissions όταν δεν υπάρχει OWNER. | CHK-009 / SEC-011 / TM-006 |
| Αντικατάσταση Patient ID ή path Clinic ID | Επιτρέπεται μόνο ο συνδυασμός authorized Clinic και resource. Opaque IDs δεν αποτελούν exemption. | CHK-011 / SEC-012 / TM-005 |
| Nested parent/child substitution, εφόσον υπάρχει nested endpoint | Επαληθεύεται και parent και child ownership/relationship. | CHK-011, CHK-014 / SEC-012, SEC-018 / TM-005, TM-009 |
| Forged clinic_id σε create, conflicting tenant fields ή reparenting update | Δεν ανατίθεται object σε Clinic από μη έμπιστο input. Καμία unauthorized ownership αλλαγή. | CHK-012 / SEC-012, SEC-017 / TM-005, TM-009 |
| Cross-clinic create/update/delete attempt | Καμία unauthorized mutation ή partial write. Delete tests μόνο αν διαθέσιμο endpoint. | CHK-011, CHK-012, CHK-020 / SEC-012, SEC-018 / TM-005, TM-009 |
| Missing έναντι inaccessible Patient | Consistent public not-found semantics, χωρίς ύπαρξη/πεδία άλλης Clinic. | CHK-011, CHK-026 / SEC-012, SEC-019 / TM-005, TM-013 |
| Mixed-clinic Patient list/search/count/pagination | Μόνο allowed rows και scoped totals/metadata. Δεν απαιτείται export implementation. | CHK-013 / SEC-012, SEC-019 / TM-005, TM-013 |
| Role change ή membership removal με ίδιο JWT | Εφαρμόζεται το τρέχον DB authorization στο επόμενο request. | CHK-008, CHK-009, CHK-010 / SEC-010, SEC-011 / TM-006 |
| Operations ανά role | Exact `patients.read`, `patients.create`, `patients.update_basic` checks. OWNER-only `patients.delete` μόνο αν διατίθεται delete. | CHK-009, CHK-010 / SEC-011 / TM-006, TM-008 |
| Unauthorized fields, invalid payload ή linked-ID mismatch μέσα στο released scope | Controlled error χωρίς mass assignment, leakage ή partial mutation. | CHK-014, CHK-015, CHK-024, CHK-026 / SEC-012, SEC-017, SEC-019 / TM-009, TM-013 |

Το σωστό OWNER clinical access μέσα στην ίδια Clinic παραμένει εγκεκριμένο. Η Patient εργασία δεν δημιουργεί clinical endpoints ή Doctor profile για να το επιδείξει.

## 8. Ξεχωριστά release gates

### 8.1 Synthetic-data demo

Πριν από κάθε επίδειξη απαιτούνται πραγματικός έλεγχος CHK-046, προστασία secrets και controlled API/DB exposure. Ελέγχονται τα CHK-033/CHK-040 και η ασφαλής χρήση δικτύου ανάλογα με την πραγματική topology. Παραμένει απαγορευμένη public production χρήση.

Καταγράφονται relevant foundation/feature test results για το release commit μέσω CHK-047 και scoped release review μέσω CHK-048. Παρουσιάζονται μόνο implemented features με δηλωμένα gaps. Test-only authorization routes δεν εκτίθενται ως production functionality.

Δεν απαιτείται enterprise infrastructure, production TLS rollout, external audit product ή πλήρες production backup tooling μόνο για απομονωμένη συνθετική επίδειξη. Η controlled έκθεση και η προστασία credentials παραμένουν υποχρεωτικές. Ανοικτά authentication/session/logging/abuse gaps δεν παρουσιάζονται ως επιλυμένα και κάθε demo exception έχει συγκεκριμένο owner, reason και scope.

### 8.2 Feature completion

Κάθε F check της διαθέσιμης λειτουργίας χρειάζεται evidence και αποτέλεσμα έναντι της ακριβούς ερώτησης. Όπου ένα CHK καλύπτει πολλούς domains, δηλώνεται το feature-specific scope αντί να θεωρείται ότι ολοκληρώθηκαν όλα τα domains.

Για BACKEND-02C εφαρμόζονται οι ενότητες 6–7: **πραγματικά Patient endpoint negative tests πρέπει να έχουν εκτελεστεί πριν feature completion**. Δεν αρκεί η ύπαρξη test sources ή η επιτυχία μόνο των test-only foundation routes. Ανεπίλυτο ουσιώδες Patient authorization/isolation gap μπλοκάρει την ολοκλήρωση του feature.

Ένα feature μπορεί να ολοκληρωθεί για controlled synthetic χρήση με χωριστά καταγεγραμμένα production-only gaps. Αυτό δεν το καθιστά production-ready. Δεν προστίθενται εκτός scope Medical Records/Portal/export/infrastructure εργασίες για να κλείσουν προληπτικά όλα τα R checks.

### 8.3 Future real-data production

Η παραγωγή και τα πραγματικά patient δεδομένα παραμένουν μη εξουσιοδοτημένα σήμερα. Πριν οποιαδήποτε μετάβαση απαιτούνται:

- Όλα τα SEC P0 και τα SEC P1 των διαθέσιμων λειτουργιών, με ελέγξιμο evidence έναντι acceptance criteria.
- Πραγματικό resource isolation, role/field authorization και same-clinic relationship integrity σε released APIs.
- Εγκεκριμένα onboarding/password/session και, όπου υπάρχει Portal, OTP/identity-separation controls.
- Validation/abuse controls, safe responses/errors και privacy-safe logs/audit.
- Verified production transport, private DB/admin exposure, least privilege, secrets, hardened deployment και dependency assurance.
- Protected backups, isolated restore, incident procedures και ορισμένοι operational owners.
- Data-lifecycle/governance/privacy assessment χωρίς δήλωση αυτόματης GDPR συμμόρφωσης.
- Επίλυση σχετικών open decisions, τεκμηριωμένο release review και νέα ρητή έγκριση project owner για συγκεκριμένο deployment, σκοπό και data use.

Τα gates ακολουθούν την ενότητα 9 του SECURITY-REQUIREMENTS.md και την ενότητα 16 του SECURITY-ARCHITECTURE.md. Successful tests ή completion του checklist δεν παρέχουν μόνα τους παραγωγική άδεια ή νομική συμμόρφωση. Η SEC-028 παραμένει production blocker, παρότι η προδιαγραφή §31 αναφέρει backups/recovery ως future extension· χρειάζεται specification alignment πριν σχετική υλοποίηση.

## 9. CHK → SEC → TM → implementation/test/evidence traceability

Κάθε καταχώριση της ενότητας 5 περιλαμβάνει SEC/TM IDs, implementation evidence ή ρητή απουσία του και verification method. Τα E/T IDs επιλύονται στην ενότητα 4. Το THREAT-MODEL.md ορίζει τα σενάρια· το παρόν δεν αλλάζει τη severity/likelihood τους ή τις SEC προτεραιότητες.

| Παράδειγμα trace | Implementation/test evidence και verification gap |
|---|---|
| CHK-008 → SEC-010 → TM-005/TM-006 | E03 και T04 αφορούν membership foundation. Το release run καταγράφεται χωριστά. |
| CHK-011 → SEC-012 → TM-005 | Patient scoped service/query και two-clinic endpoint tests είναι ακόμη μελλοντικά. Δεν επινοείται υπάρχον test filename. |
| CHK-017 → SEC-013/SEC-018/SEC-021 → TM-009/TM-010 | Approved acting User/responsible Doctor απόφαση· schema, workflow και tests pending. |
| CHK-022 → SEC-015/SEC-020 → TM-018 | OTP implementation/tests απουσιάζουν. Documentation δεν μετρά ως enforcement. |
| CHK-044 → SEC-028 → TM-016 | Χρειάζεται πραγματικό isolated restore record, όχι test DB rollback. |
| CHK-047/CHK-048 → SEC-032 → TM-001 έως TM-018 | Release-level evidence συνδέει τα applicable checks με ακριβές commit/environment, results και reviewer. |

Οι έλεγχοι δεν είναι αναγκαστικά one-to-one με SEC ή TM. Ένα framework/control μπορεί να καλύπτει πολλαπλά threats και οι SEC-030/SEC-031 έχουν οριζόντιο governance scope. Όλα τα SEC-001–SEC-032 και TM-001–TM-018 αναφέρονται σε αυτό το checklist. Τα CHK IDs παραμένουν stable ακόμη όταν εξελίσσεται η implementation κατάσταση.

## 10. Reusable release verification record

Το παρακάτω είναι **κενό template**, όχι εκτελεσμένο record ή approval. Συμπληρώνεται σε χωριστό εγκεκριμένο release artifact. Δεν περιλαμβάνονται πραγματικά secrets ή sensitive datasets στα evidence.

| Πεδίο | Προς συμπλήρωση |
|---|---|
| Release / feature | Αναγνωριστικό και scope |
| Commit / branch | Ακριβές reviewed commit και branch |
| Checklist version / baseline | Έκδοση παρόντος εγγράφου |
| Ημερομηνία / reviewer | Πότε και ποιος ελέγχει |
| Environment | D/F/R, topology, DB/test target και βασική configuration χωρίς secrets |
| Data classification | Επιβεβαίωση synthetic-only για D/F· real data σήμερα μη εξουσιοδοτημένα |
| Available endpoints / excluded features | Τι διατίθεται και τι δεν περιλαμβάνεται |
| Commands / procedures | Ακριβείς εντολές ή runbook steps που πράγματι εκτελέστηκαν |
| Raw results / evidence location | Ασφαλείς αναφορές σε outputs, exit codes, failures/skips και operational evidence |
| Exceptions / blockers | CHK IDs, reason, owner, scope και επόμενο review |
| Gate outcome / approver | Demo / feature / future production αποτέλεσμα και αρμόδιος |

| CHK ID | Scope | Implementation status | Verification result | Method / command | Evidence / actual result | Reviewer / date | Exception / next review |
|---|---|---|---|---|---|---|---|
| CHK-___ | Προς συμπλήρωση | Προς συμπλήρωση βάσει evidence | Not verified | Προς συμπλήρωση | Καμία εκτέλεση από το template | Προς συμπλήρωση | Προς συμπλήρωση |

Για κάθε check καταγράφονται αναμενόμενο και πραγματικό αποτέλεσμα, όχι μόνο ένα exit code ή test count. `Yes` σημαίνει επαρκή κάλυψη της συγκεκριμένης ερώτησης. Ατελές ή μη εκτελεσμένο verification παραμένει `Not verified`. `Not Applicable` χρειάζεται αιτιολόγηση applicability και reviewer, όχι συμπλήρωση για να μειωθούν οι blockers.

## 11. Open decisions, residual risks, exceptions και review triggers

### 11.1 Open decisions

1. Ακριβές BACKEND-02C endpoint/field scope και AMKA rules. Δεν έχει εγκριθεί uniqueness/global identity policy.
2. Patient deletion/retention/history και any global linkage. `patients.delete` permission δεν επιβάλλει hard deletion.
3. Bootstrap/invitations, activation/recovery και MFA policy.
4. Password bounds/work factor, session/revocation, lifetimes και token-purpose/issuer/audience αποφάσεις.
5. Clinical acting User/responsible Doctor schema και attribution rules. OWNER clinical permission παραμένει εγκεκριμένη.
6. Doctor assignment, appointment concurrency και Payment–Appointment–Patient consistency.
7. Portal eligibility, destination verification, provider/channel και OTP entropy/expiry/attempt/resend policies.
8. Request/throttle limits, proxy trust και single/multi-instance assumptions.
9. Audit event catalogue, denied attempts, retention/access/integrity και audit-failure behavior.
10. Hosting/network/TLS, DB privileges/encryption, key custody και secret rotation.
11. Dependency remediation, backup RPO/RTO/retention και incident ownership.
12. Privacy responsibilities, data purposes/rights/providers/transfers και release reviewer/approval διαδικασία.

Αριθμητικές τιμές και νομικά συμπεράσματα δεν επινοούνται. OWNER full declared permissions στη δική του Clinic και clinic-local role addition είναι κλειστές αποφάσεις, όχι unresolved επιλογές. Δεν εγκρίνεται Doctor profile μόνο από OWNER role.

### 11.2 Residual risks και exceptions

Παραμένουν public registration, inactive-user token issuance, copied-token replay μετά local logout, απουσία τεκμηριωμένων rate limiting/audit controls και άγνωστη operational προστασία. Clinic/RBAC foundations δεν εγγυώνται Patient resource isolation. Patient, clinical, relationship και OTP controls είναι μελλοντικά στο αντίστοιχο scope. Η νόμιμη application permission του OWNER δεν εξαλείφει insider misuse risk.

Κάθε demo exception καταγράφει CHK/SEC/TM links, υπεύθυνο, αιτιολόγηση, affected environment, προσωρινό περιορισμό και review trigger/date. Δεν μετατρέπει status/result σε Implemented/Yes. Δεν παρακάμπτει ουσιώδη security acceptance criteria διαθέσιμου feature ούτε επιτρέπει real data ή δημόσια παραγωγή χωρίς ξεχωριστή έγκριση.

Δεν απαιτούνται πρόσθετα enterprise προϊόντα, microservices ή RLS για να επιδειχθεί ένα απομονωμένο synthetic thesis foundation. Δεν παρουσιάζεται όμως η απουσία τους ως γενική απόδειξη παραγωγικής ασφάλειας. Το επίπεδο operational ελέγχων καθορίζεται από το deployment και το threat model.

### 11.3 Review triggers

Review γίνεται σε νέα/μεταβαλλόμενα endpoints, schemas, relationships, roles/memberships, auth/session/password/OTP flows, clinical attribution, exports/analytics/jobs και providers. Γίνεται επίσης σε αλλαγές Docker/dependencies/network/secrets/DB privileges/logging/audit/backup, incident ή failed verification.

Πρόταση πραγματικών δεδομένων ή public production ενεργοποιεί πλήρες production-readiness review και νέα ρητή έγκριση. Ενημερώνονται baseline, evidence, checklist statuses, release applicability και τα σχετικά security documents με εγκεκριμένο scope. Test source δεν αντικαθιστά νέα execution evidence όταν αλλάξει implementation ή περιβάλλον.

## 12. Ιστορικό εκδόσεων

| Έκδοση | Ημερομηνία | Μεταβολή |
|---|---|---|
| 1.0 | 2026-10-31 | SECURITY-00D: 48 stable checks σε 15 ομάδες, χωριστά implementation/result fields, BACKEND-02C subset και Patient negative-test matrix, D/F/R gates, traceability και release record template. Όλα τα αρχικά verification results Not verified· χωρίς application test runs, migrations ή production approval. |
