# Συμβόλαιο Patient — BACKEND-02C

Ημερομηνία: 2026-10-31. Κατάσταση: τεκμηρίωση εγκεκριμένων αποφάσεων και προτεινόμενου σχεδιασμού, χωρίς υλοποίηση.

Baseline επιθεώρησης: branch `feature/clinic-authorization`, HEAD `e280394400a95b0c78191d0ff57e92b38670ec91`. Στο Step 1 το working tree ήταν αρχικά καθαρό. Στο Step 1B επαληθεύτηκε ότι μοναδική αλλαγμένη/untracked διαδρομή ήταν το παρόν αρχείο. Το Step 1B ενημερώνει μόνο αυτό το έγγραφο. Δεν εκτελέστηκαν application/security tests, migrations ή εγκαταστάσεις εξαρτήσεων.

## Πηγές και σημερινή κατάσταση

- [System Specification](../system-specification.md): FR-PAT-001–005, FR-AUTH-004, FR-CLINIC-003, NFR-001–003, NFR-008–009 και §§18–24.
- [Security Requirements](../security/SECURITY-REQUIREMENTS.md): απαιτήσεις SEC και εγκεκριμένο clinic-local RBAC.
- [Threat Model](../security/THREAT-MODEL.md): κυρίως TM-005, TM-006, TM-009 και TM-013.
- [Security Architecture](../security/SECURITY-ARCHITECTURE.md): §§6–12, όρια service/ORM και απομόνωση tenants.
- [Security Checklist](../security/SECURITY-CHECKLIST.md): §§6–8, BACKEND-02C acceptance subset και προτεινόμενα negative tests.

**CURRENT:** Υπάρχουν [Clinic](../../backend/app/db/models/clinic.py), [ClinicMembership](../../backend/app/db/models/clinic_membership.py), [MembershipRole](../../backend/app/db/models/membership_role.py), [permission policy](../../backend/app/core/permissions.py) και [authentication/clinic dependencies](../../backend/app/api/deps.py). Οι dependencies ελέγχουν ενεργό staff User, membership στην αιτούμενη Clinic και permissions της συγκεκριμένης membership. Δεν υπάρχει OWNER ή superuser bypass.

Οι [permission tests](../../backend/tests/test_permissions.py), [clinic context tests](../../backend/tests/test_clinic_context.py), [authorization tests](../../backend/tests/test_clinic_authorization.py) και [constraint tests](../../backend/tests/test_clinic_membership_constraints.py) παρέχουν επιθεωρημένο test source. Οι clinic authorization routes τους είναι test-only. Τα [fixtures](../../backend/tests/conftest.py) επιτρέπουν συγκεκριμένη απομονωμένη PostgreSQL test DB, εκτελούν Alembic upgrade όταν ζητηθούν και χρησιμοποιούν rollback ανά test. Η ύπαρξή τους δεν αποδεικνύει επιτυχή εκτέλεση.

**PLANNED:** Όλα τα Patient models, schemas, routes, services, constraints και endpoint tests του παρόντος. Το baseline έχει μόνο foundation tables και migration head `a807f733a8e3`, μετά το `71eda1fd3061`· δεν επαληθεύτηκε ζωντανή DB. Η [εφαρμογή](../../backend/app/main.py) δεν εφαρμόζει σήμερα το `API_PREFIX` στο router mounting.

Οι προηγούμενες security πηγές άφηναν ανοικτά AMKA uniqueness και global identity. Οι ρητές εγκρίσεις των Steps 1/1B επιλύουν clinic-local uniqueness, ανεξάρτητα clinic records και τους τεχνικούς κανόνες που σημειώνονται παρακάτω ως εγκεκριμένοι. Δεν αλλάζουν τα security statuses των πηγών ούτε αποτελούν έγκριση παραγωγής. Η §N διακρίνει τις επιλυμένες από τις εκκρεμείς επιλογές.

## A. Πεδίο και εξαιρέσεις

Εγκεκριμένο πεδίο: δημιουργία, ανάγνωση, λίστα/αναζήτηση και ενημέρωση βασικών δημογραφικών/στοιχείων επικοινωνίας Patient, μέσα σε μία εξουσιοδοτημένη Clinic.

Επιτρέπονται αποκλειστικά συνθετικά δεδομένα. Απαγορεύονται πραγματικά στοιχεία ασθενών και δημόσια παραγωγική διάθεση. Η μελλοντική ολοκλήρωση του feature δεν αποδεικνύει production readiness ή GDPR συμμόρφωση.

Δεν περιλαμβάνονται Medical Records, Appointments, Payments, Patient Portal/OTP, frontend, exports, analytics, global matching/merging, μεταφορά Patient μεταξύ Clinics, DELETE, soft deletion ή archival. Τα FR-PAT-006–007 παραμένουν για μεταγενέστερα domains. Πλήρες audit implementation αναβάλλεται.

## B. Ownership και invariants απομόνωσης

1. Κάθε Patient ανήκει σε ακριβώς μία Clinic. Δεν υπάρχει Patient χωρίς clinic ownership.
2. Το ίδιο πραγματικό πρόσωπο μπορεί να έχει ανεξάρτητα records σε διαφορετικές Clinics, χωρίς global linking, αντιστοίχιση ή συγχρονισμό στοιχείων.
3. Το `clinic_id` ορίζεται αποκλειστικά από trusted authenticated membership. Το path επιλέγει αιτούμενο context, αλλά μόνο του δεν αποδεικνύει εξουσιοδότηση.
4. Κάθε read/update περιορίζεται ταυτόχρονα από authorized `clinic_id` και `patient_id`. Lists, searches, counts και pagination metadata χρησιμοποιούν το ίδιο clinic scope.
5. Κανένα body δεν επιτρέπεται να ορίζει `id`, `clinic_id`, timestamps ή actor fields. Απορρίπτονται ακόμη και αν συμφωνούν με τον server. Ordinary PATCH δεν αλλάζει ownership.
6. OWNER και `is_superuser` δεν παρακάμπτουν clinic boundaries. Roles συνδυάζονται μόνο στην ίδια membership, ποτέ μεταξύ Clinics.
7. Ανύπαρκτο και μη προσβάσιμο Patient έχουν αδιαχώριστο public 404: ίδιο status, body και απουσία identifying metadata. Δεν προηγείται global lookup που αποκαλύπτει ύπαρξη.
8. Το AMKA δεν αποτελεί authentication, global lookup key ή απόδειξη δικαιώματος πρόσβασης.

## C. Συμβόλαιο πεδίων

Η κατηγοριοποίηση και οι παρακάτω ρητοί κανόνες names/phone/email/AMKA είναι εγκεκριμένοι. Όπου αναφέρεται «προτείνεται», πρόκειται για σχεδιασμό προς review, όχι πρόσθετη έγκριση.

| Πεδίο | Κατηγορία | Σημασία / σχεδιασμός |
|---|---|---|
| `first_name` | Υποχρεωτικό | String, trim περιβάλλοντος whitespace, απόρριψη blank μετά το trim, έως 100 χαρακτήρες. |
| `last_name` | Υποχρεωτικό | String, trim περιβάλλοντος whitespace, απόρριψη blank μετά το trim, έως 100 χαρακτήρες. |
| `date_of_birth` | Προαιρετικό | Προτείνεται nullable date, χωρίς εξαγωγή από AMKA. |
| `phone` | Προαιρετικό | Nullable string, trim περιβάλλοντος whitespace, έως 25 χαρακτήρες, χωρίς Greece-only format ή verified ownership. |
| `email` | Προαιρετικό | Nullable, validated email format, χωρίς uniqueness ή verified ownership· δεν είναι staff identity. |
| `amka` | Προαιρετικό | Nullable string ακριβώς 11 ASCII ψηφίων όταν παρέχεται, μοναδικό μόνο μέσα στην Clinic. |
| `id` | Server-controlled | Μοναδικό εσωτερικό ID. Προτείνεται Integer PK όπως στα υπάρχοντα models. |
| `clinic_id` | Server-controlled | Υποχρεωτικό clinic FK από validated membership. |
| `created_at` | Server-controlled | Χρόνος δημιουργίας· προτείνεται μη nullable timezone-aware timestamp. |
| `updated_at` | Server-controlled | Χρόνος επιτυχούς ενημέρωσης· προτείνεται μη nullable timezone-aware timestamp. |

Δεν εγκρίνεται πρόσθετη συλλογή clinical notes, διευθύνσεων, demographic categories ή emergency contacts. Phone/email δεν αποκτούν uniqueness από αυτό το συμβόλαιο.

## D. AMKA: αποθήκευση, uniqueness και privacy

Εγκεκριμένα: προαιρετικό string ακριβώς 11 ASCII ψηφίων (`0`–`9`) όταν παρέχεται, με διατήρηση αρχικών μηδενικών και nullable clinic-local uniqueness. Δεν επιβάλλεται global uniqueness ή identity linkage. Ίδια τιμή μπορεί να υπάρχει στην A και στην B χωρίς conflict ή αποκάλυψη της άλλης Clinic.

Προτεινόμενη PostgreSQL υλοποίηση: named `UNIQUE (clinic_id, amka)` με τη συνήθη συμπεριφορά διακριτών NULLs, ώστε πολλοί Patients της ίδιας Clinic να μπορούν να μην έχουν AMKA. Δεν χρησιμοποιείται `NULLS NOT DISTINCT`. Ο κανόνας επιβάλλεται στη DB και καλύπτει concurrent inserts/updates· ένας προληπτικός service lookup δεν αρκεί.

Missing AMKA στη δημιουργία ή explicit NULL για εκκαθάριση αποθηκεύεται ως SQL NULL. Omitted AMKA σε PATCH διατηρεί την υπάρχουσα τιμή. Empty ή whitespace-only strings απορρίπτονται· δεν αποθηκεύονται ως τιμές ούτε μετατρέπονται σιωπηρά σε NULL. Τιμή με whitespace δεν ικανοποιεί τον κανόνα των ακριβώς 11 ASCII ψηφίων. Δεν εφαρμόζεται checksum, registry lookup ή real-identity verification σε αυτή τη φάση. Οι ίδιοι κανόνες ισχύουν σε create/update.

Πλήρες AMKA αποκλείεται από ordinary responses και logs, ακόμη και για OWNER. Δεν προστίθεται AMKA search ή public verification endpoint. Conflict δεν περιλαμβάνει τιμή AMKA, Patient ID, Clinic άλλου tenant ή raw constraint/SQL details. Προτείνεται generic 409 για duplicate μέσα στην authorized Clinic· το ακριβές error envelope παραμένει προς έγκριση. Record άλλης Clinic δεν επηρεάζει την έκβαση.

String storage δεν σημαίνει application encryption ή επαρκή προστασία πραγματικών δεδομένων. Encryption/key custody απαιτούν ξεχωριστό σχεδιασμό πριν από real-data χρήση. Απλό hashing δεν παρουσιάζεται ως πλήρης λύση privacy ή ανακτήσιμης αποθήκευσης.

## E. Input/output schemas και ελαχιστοποίηση

Τα ονόματα schemas είναι προτάσεις, όχι υπάρχοντα Python αντικείμενα.

| Schema | Προτεινόμενο περιεχόμενο |
|---|---|
| `PatientCreate` | `first_name`, `last_name` και μόνο τα τέσσερα εγκεκριμένα optional fields. |
| `PatientUpdate` | Μόνο τα έξι business fields. Empty PATCH απορρίπτεται. Omitted πεδίο διατηρείται, explicit NULL εκκαθαρίζει optional πεδίο. Required names δεν δέχονται NULL ή blank μετά το trim. |
| `PatientSummary` | ID και ονόματα. Phone ή ημερομηνία γέννησης μόνο αν εγκριθεί συγκεκριμένη ανάγκη διάκρισης στη λίστα. |
| `PatientDetail` | ID, ονόματα και αναγκαία demographic/contact fields, ενδεχομένως timestamps. Ποτέ πλήρες AMKA. |
| `PatientPage` | Λίστα summaries και εγκεκριμένα pagination metadata. Totals μόνο αν επιλεγούν και πάντα scoped. |

Επιτρέπονται updates μόνο στα εγκεκριμένα mutable fields. Απορρίπτονται `id`, `clinic_id`, timestamps, actor IDs και clinical fields. Προτείνεται επιπλέον απόρριψη κάθε άλλου extra input field αντί σιωπηρής αγνόησης. Κάθε output έχει explicit allowlist, χωρίς αυτόματο relationship serialization ή clinical fields. Αν χρειαστεί μελλοντικά ένδειξη ύπαρξης AMKA, masking ή ειδική προβολή, απαιτείται ξεχωριστή έγκριση· δεν προστίθεται εδώ.

## F. Endpoint και authorization contracts

Οι παρακάτω διαδρομές και permissions είναι εγκεκριμένες, χωρίς prefix στις συγκεκριμένες διαδρομές και χωρίς αλλαγή της τρέχουσας ρύθμισης `API_PREFIX` ή του mounting των υπαρχόντων routes.

| Endpoint | Request | Permission | Προτεινόμενη επιτυχία / response |
|---|---|---|---|
| `POST /clinics/{clinic_id}/patients` | Create body | `patients.create` | 201, `PatientDetail` χωρίς AMKA |
| `GET /clinics/{clinic_id}/patients` | Search/pagination query | `patients.read` | 200, `PatientPage` |
| `GET /clinics/{clinic_id}/patients/{patient_id}` | Path IDs | `patients.read` | 200, `PatientDetail` |
| `PATCH /clinics/{clinic_id}/patients/{patient_id}` | Partial update body | `patients.update_basic` | 200, `PatientDetail` |

Κάθε route καλεί current active staff validation, clinic membership και `require_permission` για την ακριβή operation πριν από Patient lookup/service invocation. Το API χειρίζεται HTTP, όχι business rules.

| Role της τρέχουσας Clinic | Read/list/search | Create | Update basic | Declared delete |
|---|---|---|---|---|
| OWNER | Ναι | Ναι | Ναι | Ναι, χωρίς endpoint |
| DOCTOR | Ναι | Ναι | Ναι | Όχι |
| SECRETARY | Ναι | Ναι | Ναι | Όχι |
| Χωρίς roles | Όχι | Όχι | Όχι | Όχι |

Ο OWNER διατηρεί όλες τις declared permissions εντός Clinic. Η `patients.delete` παραμένει στο catalog· δεν εισάγεται DELETE ούτε περιορίζονται άλλες υπάρχουσες permissions. Multi-role union παραμένει ακριβώς όπως στην τρέχουσα πολιτική.

## G. Αναζήτηση και bounded pagination

Εγκεκριμένα search fields: `first_name`, `last_name`, `phone`. Όλα τα αποτελέσματα και counts περιορίζονται στην authorized Clinic πριν από pagination. Δεν προστίθενται αναζητήσεις σε email, AMKA ή άλλες Clinics.

Εγκεκριμένο pagination: default page size 20, maximum page size 100 και σταθερή αύξουσα ταξινόμηση κατά Patient ID. Όλα τα αποτελέσματα και metadata είναι tenant-scoped. Query parameter names, offset/cursor επιλογή και ακριβή metadata παραμένουν ανοικτά. Προτείνεται απλό limit/offset. Η συμπεριφορά σε out-of-range page size χρειάζεται τελική επιλογή, χωρίς ποτέ υπέρβαση του maximum. Δεν εγγυάται snapshot consistency μεταξύ διαδοχικών σελίδων με concurrent writes.

Εγκεκριμένο search: case-insensitive matching στα τρία search fields, bounded input και escaping SQL LIKE wildcards για literal matching. Accent sensitivity, detailed normalization, prefix/substring matching, συνδυασμός όρων/πεδίων, phone matching πέρα από το case-insensitive/literal contract, κενό query και αριθμητικό query-length bound παραμένουν ανοικτά. Parameterized ORM queries είναι υποχρεωτικά ανεξάρτητα από το matching που θα εγκριθεί. Τα search inputs ενδέχεται να περιέχουν προσωπικά στοιχεία· δεν αντιγράφονται ανεξέλεγκτα σε access/error logs. Πλήρες AMKA δεν εμφανίζεται στα search results.

## H. Validation και ασφαλή errors

**CURRENT foundation:** Missing/invalid/expired credentials ή nonexistent User οδηγούν σε 401. Inactive User σε 403. Inaccessible/nonexistent Clinic σε κοινό 404. Απουσία permission σε 403. Τα υπάρχοντα DB error propagation tests δεν αποδεικνύουν ασφαλή response/log redaction.

**PLANNED Patient:** Missing και inaccessible Patient οδηγούν στο ίδιο 404, χωρίς global existence check. Permission denial προηγείται resource lookup και δεν εξαρτάται από την ύπαρξη Patient. Αποτυχία δεν αφήνει mutation ή partial write.

Προτείνονται 422 για invalid inputs, 409 για το εγκεκριμένο local AMKA conflict και sanitized 5xx για απρόβλεπτη DB αποτυχία. Ακριβή envelopes και μηνύματα αποφασίζονται πριν την υλοποίηση. Validation errors δεν ανακλούν ολόκληρο input, AMKA ή forbidden-field values. Αποκλείονται SQL, connection strings, stack traces, tokens και raw exception parameters από public responses και logs.

Εγκεκριμένοι validation κανόνες: names με trim, nonblank και maximum 100 χαρακτήρες ανά πεδίο· phone με trim και maximum 25 χαρακτήρες χωρίς Greece-only format· validated email χωρίς uniqueness· AMKA όπως στην §D· pagination 20/100 όπως στην §G. Empty PATCH απορρίπτεται, required names δεν δέχονται NULL/blank και optional fields εκκαθαρίζονται με explicit NULL, διακριτό από omission. Προτείνεται επιπλέον ημερομηνία γέννησης όχι στο μέλλον· date bounds, υπόλοιπα string bounds και μη εγκεκριμένη normalization παραμένουν ανοικτά. Δεν συνάγονται ηλικία, φύλο ή eligibility από AMKA.

## I. Database constraints, indexes και migration plan

Προτεινόμενη υλοποίηση μετά από έγκριση των ανοικτών επιλογών:

- `patients` με PK, μη nullable `clinic_id` FK προς `clinics.id`, required names και server timestamps· optional fields nullable.
- Named local AMKA uniqueness όπως στην §D, χωρίς global unique index.
- Προτείνεται restrictive Clinic FK deletion behavior χωρίς cascade διαγραφής Patients και explicit `Clinic.patients` / `Patient.clinic` relationships. Αυτό δεν θεσπίζει retention policy.
- Προτείνεται index `(clinic_id, id)` για scoped λίστα. Ο unique AMKA index εξυπηρετεί τον αντίστοιχο local κανόνα. Search indexes επιλέγονται μετά το matching contract· ένα απλό B-tree δεν θεωρείται εκ των προτέρων λύση κάθε substring search.
- Length/check constraints ευθυγραμμίζονται με τα εγκεκριμένα names 100, phone 25 και nullable AMKA ακριβώς 11 ASCII ψηφίων. Η ακριβής SQL έκφραση/check ονομάτων, οι τύποι/μήκη email και οι υπόλοιπες ανοικτές επιλογές χρειάζονται review πριν τη migration. Δεν εισάγεται speculative composite key ή σχέση με μελλοντικά domains.

Η αλλαγή απαιτεί νέα Alembic migration με parent `a807f733a8e3`, model export στο metadata και επιθεώρηση upgrade/downgrade. Δεν τροποποιούνται παλιές migrations. Μελλοντικό verification περιλαμβάνει isolated synthetic upgrade, constraints, downgrade και re-upgrade, καθώς και concurrent uniqueness tests. Downgrade που αφαιρεί Patient table καταστρέφει τα δεδομένα του και ελέγχεται μόνο σε disposable test DB. Καμία τέτοια ενέργεια δεν εκτελείται στην παρούσα εργασία.

FK/uniqueness προστατεύουν integrity, όχι από μόνες τους tenant reads. Δεν υπάρχει evidence RLS. Σύμφωνα με την Security Architecture §9.3, RLS μπορεί να αξιολογηθεί ξεχωριστά και δεν αποτελεί προϋπόθεση αυτού του module ή υποκατάστατο API/service/ORM scope.

## J. Service transactions και rollback

Προτείνεται μικρό Patient service με explicit trusted actor/membership context, object authorization και focused tenant-scoped ORM queries. Κανένα global mutable current Clinic και κανένα generic repository framework δεν απαιτούνται. Εναλλακτικοί callers δεν αποκτούν authority από ένα αυθαίρετο `clinic_id` argument.

Η atomic μονάδα create/update περιλαμβάνει validation, scoped lookup όπου απαιτείται, αλλαγή και flush/commit. Το service κατέχει το mutation transaction boundary· route/query helpers δεν κάνουν ανεξάρτητα commits. Σφάλμα, συμπεριλαμβανομένου concurrent AMKA conflict, οδηγεί σε rollback πριν τη μετατροπή σε ασφαλές domain/HTTP error. Μετά αποτυχία ελέγχεται και η DB κατάσταση.

Το υπάρχον Session μπορεί να έχει αρχίσει transaction από authentication/membership queries. Η υλοποίηση πρέπει να το λάβει υπόψη, χωρίς τυφλό δεύτερο `Session.begin()`. Ακριβής τεχνική διαχείρισης και χειρισμός concurrent updates/lost updates παραμένουν προς review. Δεν προστίθενται external calls ή notification side effects.

## K. Προτεινόμενα audit events — αναβολή υλοποίησης

Προς σχεδιασμό: `patient.created`, `patient.basic_updated`, αποτυχημένη/denied mutation και, αν δικαιολογηθεί από σκοπό πρόσβασης, sensitive read. Προτείνονται actor User ID, trusted Clinic ID, action, επιτρεπόμενο target ID, timestamp, outcome και correlation ID. Για denied inaccessible resources δεν επιβεβαιώνεται πραγματικό target άλλης Clinic.

Ο actor προκύπτει από authenticated identity, ποτέ από body. Προτείνεται καταγραφή ονομάτων μεταβληθέντων πεδίων, χωρίς values, πλήρες AMKA, clinical content ή request dump. Όταν υλοποιηθεί επιτυχές mutation audit, πρέπει να συνδέεται αξιόπιστα με το commit και να μην καταγράφει rollback ως επιτυχία.

Ακριβές event schema, persistence, access/integrity, retention, failure policy και read-event catalogue είναι ανοικτά. Πλήρης αποθήκευση audit και actor attribution implementation αναβάλλονται. Δεν προστίθενται τώρα actor columns ή audit infrastructure. Timestamps δεν αποτελούν πλήρες audit trail· SEC-021/CHK-030 παραμένουν εκκρεμότητες, ιδιαίτερα πριν από παραγωγή.

## L. Acceptance matrix δύο Clinics και πολλαπλών roles

Όλες οι γραμμές είναι **μελλοντικά acceptance tests, όχι εκτελεσμένα tests**. Χρησιμοποιούνται συνθετικοί Users/Patients στις A/B, πραγματικά Patient endpoints και οι πραγματικές dependencies. Κάθε denied/failed mutation συνοδεύεται από assertion ότι η DB δεν άλλαξε.

| Περίπτωση | Αναμενόμενο |
|---|---|
| Missing/malformed/expired/invalid-signature token | 401, χωρίς Patient data ή mutation. |
| Nonexistent/inactive User | Τρέχον 401/403 αντίστοιχα. |
| Χωρίς membership στην B | Ίδιο clinic 404 με nonexistent Clinic. |
| Membership χωρίς roles | 403 για όλες τις operations. |
| OWNER A ζητά Patient B κάτω από path A | Ίδιο Patient 404 με ανύπαρκτο ID. |
| OWNER A αλλάζει path σε B χωρίς membership | Clinic 404, χωρίς OWNER bypass. |
| Superuser χωρίς membership ή κατάλληλο role | Κανένα bypass· 404 ή 403 ανά το υπάρχον contract. |
| Memberships και στις A/B, αλλά Patient B κάτω από A | Patient 404, ακόμη κι αν ο User δικαιούται ξεχωριστά πρόσβαση στην B. |
| OWNER A + SECRETARY B | Μόνο SECRETARY permissions στην B· καμία μεταφορά OWNER authority. |
| DOCTOR + SECRETARY στην ίδια Clinic | Ακριβής τοπική ένωση, χωρίς OWNER-only permissions. |
| Κάθε role για POST/GET/list/PATCH | Ακριβής εφαρμογή της §F. |
| Role αλλαγή ή membership removal με ίδιο JWT | Εφαρμογή τρέχουσας DB εξουσιοδότησης στο επόμενο request. |
| Mixed-clinic search σε όνομα/επώνυμο/phone και pagination | Μόνο scoped rows, counts και metadata, ακόμη και σε μηδενικό αποτέλεσμα. |
| Forged id/clinic_id/timestamps/actor ή clinical fields | Rejection χωρίς mass assignment ή sensitive reflection. |
| PATCH αλλαγής ownership | Rejection, αμετάβλητη Clinic. |
| Ίδιο AMKA σε A/B | Επιτρέπεται ανεξάρτητα, χωρίς cross-clinic conflict/lookup. |
| Duplicate AMKA μέσα στην A, create ή update | Local constraint failure και ασφαλές error· κανένα ξένο record disclosure. |
| Concurrent writes ίδιου AMKA στην A | Η DB εμποδίζει duplicate committed values· loser rollback χωρίς partial writes. |
| Πολλοί Patients χωρίς AMKA στην ίδια Clinic | Επιτρέπονται NULLs χωρίς uniqueness conflict. |
| AMKA με αρχικό μηδενικό / non-ASCII ψηφία / λάθος μήκος / empty ή whitespace | Διατήρηση αρχικού μηδενικού στην έγκυρη τιμή· απόρριψη των μη έγκυρων τιμών χωρίς reflection. |
| Names με whitespace/blank/NULL και όριο 100 | Trim και έλεγχος ορίου· απόρριψη blank/NULL και υπέρβασης. |
| Phone με whitespace ή υπέρβαση 25 / invalid email | Trim phone, χωρίς Greece-only restriction· απόρριψη υπέρβασης ή invalid email· καμία verified-ownership υπόθεση. |
| Empty PATCH / omitted optional / explicit NULL | Απόρριψη empty PATCH· διατήρηση omitted πεδίου· εκκαθάριση optional με NULL, συμπεριλαμβανομένου SQL NULL για AMKA. |
| Search case/wildcards και pagination | Case-insensitive literal matching με escaped wildcards· default 20, maximum 100, αύξον ID και scoped metadata. |
| Υπόλοιπα invalid fields και ανοικτά boundaries | Αποτέλεσμα σύμφωνα με τις εκκρεμείς αποφάσεις §N αφού εγκριθούν. |
| DB failure μετά από αλλαγή | Rollback, sanitized response/logs, χωρίς misleading success. |
| List/detail/create/update outputs και failure logs | Απουσία πλήρους AMKA, clinical fields, SQL και secrets. |

Οι τρεις roles έχουν ίδιες permissions για τα τέσσερα διαθέσιμα Patient endpoints. Επομένως τα Patient tests μόνα τους δεν αποδεικνύουν όλη τη διαφορά OWNER/SECRETARY ή την ευρύτερη additive union. Διατηρούνται τα foundation matrix tests· δεν δημιουργείται DELETE ή clinical endpoint για να αποδειχθεί αυτή η διαφορά. Nested-domain tests αναβάλλονται μέχρι να υπάρχουν αντίστοιχες σχέσεις.

## M. Traceability CHK / SEC / TM

Οι αντιστοιχίσεις αφορούν το Patient scope· δεν κλείνουν ολόκληρα controls άλλων domains.

| Έλεγχος | CHK | SEC | TM |
|---|---|---|---|
| Current active staff και credentials | CHK-002, CHK-005, CHK-010 | SEC-003, SEC-006, SEC-009 | TM-001, TM-002 |
| Membership και clinic-local RBAC | CHK-008, CHK-009, CHK-010 | SEC-010, SEC-011 | TM-005, TM-006 |
| Scoped resources και trusted ownership | CHK-011, CHK-012 | SEC-012, SEC-017 | TM-005, TM-009 |
| List/search/count/pagination isolation | CHK-013 | SEC-012, SEC-019 | TM-005, TM-013 |
| Integrity και migration constraints | CHK-014, CHK-039 | SEC-012, SEC-018 | TM-009 |
| Administrative schemas και minimization | CHK-015, CHK-025 | SEC-013, SEC-019 | TM-008, TM-013 |
| Validation, safe errors και rollback | CHK-020, CHK-024, CHK-026 | SEC-017, SEC-018, SEC-019 | TM-009, TM-013 |
| Bounded search/pagination | CHK-028 | SEC-017, SEC-020 | TM-015 |
| Audit design και privacy-safe logging | CHK-030, CHK-031 | SEC-021, SEC-022 | TM-010, TM-011, TM-013 |
| Deferred lifecycle και real-data governance | CHK-032 | SEC-030, SEC-031 | TM-013, TM-016 |
| Synthetic-only και actual verification/review | CHK-046, CHK-047, CHK-048 | SEC-031, SEC-032 | Τα applicable threats παραπάνω |

Το CHK-039 καλύπτει σήμερα foundation constraints· Patient evidence χρειάζεται ξεχωριστά. CHK-021–023 και SEC-014–016 αφορούν deferred Portal· η αποθήκευση AMKA δεν τα υλοποιεί. Η απαγόρευση clinical fields εδώ δεν αποτελεί υλοποίηση Medical Records. Δεν δηλώνεται ότι εκτελέστηκε κανένα security test ή release gate.

## N. Αναβολές και ανοικτές τεχνικές αποφάσεις

**Επιλυμένα στο Step 1B:** AMKA 11 ASCII ψηφίων/SQL NULL/no checksum, names trim/nonblank/100, phone trim/25 χωρίς Greece-only format, validated non-unique email, case-insensitive literal search με wildcard escaping, pagination 20/100 και αύξον ID, empty PATCH rejection και explicit NULL clearing, καθώς και διαδρομές χωρίς προσθήκη API prefix. Audit implementation και deletion/archival παραμένουν εκτός scope, όχι ανοικτή άδεια προσθήκης τους.

Οι παρακάτω υπόλοιπες επιλογές **δεν έχουν εγκριθεί**. Απαιτείται επίλυση πριν από το αντίστοιχο implementation, χωρίς αυθαίρετες αριθμητικές τιμές. Δεν επανανοίγουν τις παραπάνω εγκρίσεις.

| Απόφαση | Σύσταση / όριο |
|---|---|
| Υπόλοιπο normalization και email storage | Accent/Unicode normalization πέρα από το εγκεκριμένο trim, email normalization/μέγιστο μήκος και phone empty-string συμπεριφορά μετά το trim. Καμία αλλαγή στο AMKA contract της §D. |
| Date validation | Προτείνεται απόρριψη μελλοντικής ημερομηνίας γέννησης· ακριβή date bounds προς έγκριση. |
| Search | Accent sensitivity, detailed normalization, prefix/substring, συνδυασμός όρων/πεδίων, phone matching λεπτομέρειες, αριθμητικό query-length bound και κενό query. Case-insensitive/literal escaping ήδη εγκεκριμένα. |
| Pagination mechanics | Offset/cursor, query names, metadata και out-of-range input handling. Default 20, maximum 100 και αύξον ID ήδη εγκεκριμένα. |
| Μη κενό PATCH χωρίς πραγματική αλλαγή | Επίδραση ίδιων τιμών στο `updated_at`. Empty PATCH rejection και optional NULL clearing έχουν ήδη εγκριθεί. |
| Exact HTTP schemas | Τελικό summary/detail allowlist, envelopes, error messages και status προτάσεις §§E–H προς review. |
| Audit | Ακριβές event schema/persistence και actor attribution workflow ανοικτά· πλήρης υλοποίηση deferred. |
| Retention/deletion | Χωριστή μελλοντική policy. Καμία hard/soft deletion ή archival σε BACKEND-02C. |
| Transactions/concurrency | Review session lifecycle και lost-update policy, χωρίς παράκαμψη του εγκεκριμένου concurrent AMKA uniqueness. |

Πριν Patient model/migration χρειάζεται review των προτεινόμενων persistence επιλογών (§§C/I): ακριβείς SQL τύποι, email μήκος/normalization όπου επηρεάζει αποθήκευση, timestamp defaults/update mechanism, named checks/indexes και FK deletion behavior. Οι κανόνες ονομάτων/phone/AMKA και clinic-local uniqueness έχουν επιλυθεί. Search mechanics, HTTP envelopes και full audit/retention δεν απαιτούν επέκταση του model εκ των προτέρων και δεν δικαιολογούν speculative columns ή features.

Παραμένουν deferred τα domains της §A, RLS ως ξεχωριστή αξιολόγηση, πλήρες audit, production encryption/key custody και operational hardening. Υπάρχοντα authentication, logging και abuse-control gaps παραμένουν δηλωμένα· δεν παρουσιάζονται ως λυμένα ούτε διευρύνουν σιωπηρά αυτή την εργασία.

## O. Φάσεις υλοποίησης και review gates

Οι παρακάτω φάσεις είναι σχέδιο επόμενων εργασιών, όχι άδεια υλοποίησης ή commits στην παρούσα εργασία.

1. `docs: define patient contract`: review του παρόντος και επίλυση των τεχνικών αποφάσεων που απαιτούνται για την επόμενη φάση.
2. `feat: add clinic-owned patient persistence`: model, explicit relationships, local AMKA constraint και reviewed Alembic migration με PostgreSQL integrity/concurrency tests. Gate: isolated synthetic upgrade/downgrade/re-upgrade evidence.
3. `feat: add scoped patient create and read`: μικρό service, schemas, routes, exact permission dependencies και πραγματικά endpoint negative tests. Gate: δύο Clinics, OWNER, superuser, safe 404 και field minimization.
4. `feat: add patient search and basic updates`: approved matching/pagination/PATCH, scoped queries και rollback tests. Gate: counts/metadata isolation, concurrent conflicts και no partial writes.
5. `docs: record patient verification`: καταγραφή πραγματικών commands/results, commit/environment, failures/skips, review και residual gaps ανά applicable CHK. Δεν υποκαθιστά tests με inspected source.

Πριν feature completion απαιτούνται εκτελεσμένα πραγματικά Patient endpoint tests και relevant foundation regressions, σύμφωνα με CHK-047/048. Κάθε ουσιώδες Patient authorization/isolation gap μπλοκάρει ολοκλήρωση. Audit και λοιπά deferred production gaps καταγράφονται χωριστά. Κανένα gate δεν επιτρέπει πραγματικά δεδομένα ή δημόσια παραγωγή χωρίς το ανεξάρτητο production review και νέα ρητή έγκριση που απαιτούν οι security πηγές.
