# Source-to-Target Mapping - Patient360 Analytics Platform

## 1. Patient Records

| Source Column | Source Type | Bronze Column | Silver Column | Transformation |
|---|---|---|---|---|
| Patient_ID | String | patient_id | patient_id | Trim, DQ: NOT NULL |
| Patient_NAME | String | patient_name | patient_name | Trim, UPPER |
| SEX | String | sex | sex | Trim, UPPER |
| State | String | state | state | Trim, UPPER |
| Age | Integer | age | age | Cast INT, DQ: 0-120 |
| Diease_name | String | disease_name | disease_name | Trim |
| Doctor_id | String | doctor_id | doctor_id | Trim |
| Doctors_name | String | doctors_name | doctors_name | Trim |
| DOB | String | dob | dob | to_date(yyyy-MM-dd) |
| Contact | String | contact | contact | Strip non-numeric |
| email | String | email | email | LOWER, DQ: email regex |
| address | String | address | address | Trim |

**Gold targets:** patient_360_master, patient_risk_summary, patient_financial_summary

---

## 2. Appointments

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| Patient_id | patient_id | patient_id | Trim |
| Appointment_id | appointment_id | appointment_id | DQ: NOT NULL |
| doctor_name | doctor_name | doctor_name | Trim |
| doctore_id | doctore_id | doctore_id | Trim |
| booking_date | booking_date | booking_date | to_date, DQ: <= today |
| department | department | department | UPPER |
| visit_type | visit_type | visit_type | LOWER |
| status(y/n) | status | status_flag | Boolean: y=True |

**Gold targets:** doctor_performance_summary, patient_360_master

---

## 3. Diagnosis

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| Record_Id | record_id | record_id | Trim |
| Patient_Id | patient_id | patient_id | Trim |
| Doctor_name | doctor_name | doctor_name | Trim |
| Doctor_Id | doctor_id | doctor_id | Trim |
| Disease_name | disease_name | disease_name | UPPER |
| diagnosis_description | diagnosis_description | diagnosis_description | Trim |
| encounter_id | encounter_id | encounter_id | Trim |
| rank | rank | rank | Cast INT |
| checkup_date | checkup_date | checkup_date | to_date |
| diagnosis_code | diagnosis_code | diagnosis_code | UPPER, DQ: NOT NULL |
| Doctor_Charge_INR | doctor_charge_inr | doctor_charge_inr | Cast DOUBLE |

**Gold targets:** patient_clinical_summary, doctor_performance_summary

---

## 4. Medication

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| medication_id | medication_id | medication_id | Trim |
| Doctor_id | doctor_id | doctor_id | Trim |
| Patient_id | patient_id | patient_id | Trim |
| encounter_id | encounter_id | encounter_id | Trim |
| medication_name | medication_name | medication_name | Trim |
| dosage | dosage | dosage | Trim |
| route | route | route | LOWER |
| start_date | start_date | start_date | to_date |
| end_date | end_date | end_date | to_date |
| is_active | is_active | is_active_flag | Derived: end_date >= today |
| Disease | disease | disease | Trim |
| medicine_price | medicine_price | medicine_price | Cast DOUBLE, DQ: >= 0 |

**Gold targets:** medication_adherence_summary, patient_clinical_summary

---

## 5. Lab Reports

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| Serial_number | serial_number | serial_number | Trim |
| Patient_id | patient_id | patient_id | Trim |
| Doctor's_id | doctors_id | doctors_id | Trim |
| lab_test_name | lab_test_name | lab_test_name | Trim |
| test_result | test_result | test_result_num | Cast DOUBLE |
| normal_range_min | normal_range_min | normal_range_min | Cast DOUBLE |
| normal_range_max | normal_range_max | normal_range_max | Cast DOUBLE |
| Booking_date | booking_date | booking_date | to_date |
| Collect_report_date | collect_report_date | collect_report_date | to_date |
| collect report(y/n) | collect_report | collect_report_flag | Boolean |
| cost | cost | cost | Cast DOUBLE |
| _(derived)_ | | lab_status | NORMAL/ABOVE_NORMAL/BELOW_NORMAL |

**Gold targets:** patient_clinical_summary, patient_risk_summary

---

## 6. Billing

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| bill_id | bill_id | bill_id | Trim |
| patient_id | patient_id | patient_id | Trim |
| Patient_name | patient_name | patient_name | Trim |
| appointment_id | appointment_id | appointment_id | Trim |
| treatment_cost | treatment_cost | treatment_cost | Cast DOUBLE, DQ: >= 0 |
| insurence_number | insurence_number | insurance_number | Trim |
| insurence_coverage | insurence_coverage | insurance_coverage | Cast DOUBLE |
| payment_status | payment_status | payment_status | UPPER |
| payment_mode(UPI/cash) | payment_mode_upi_cash_ | payment_mode | UPPER: UPI/CASH |
| Payment_Date | payment_date | payment_date | to_date |
| insurence_provider | insurence_provider | insurance_provider | Trim |
| _(derived)_ | | out_of_pocket | treatment_cost - insurance_coverage |

**Gold targets:** patient_financial_summary, kpi_summary

---

## 7. Patient History

| Source Column | Bronze Column | Silver Column | Transformation |
|---|---|---|---|
| appointment_id | appointment_id | appointment_id | Trim |
| patient_id | patient_id | patient_id | Trim |
| doctor_name | doctor_name | doctor_name | Trim |
| doctor_id | doctor_id | doctor_id | Trim |
| visit_type | visit_type | visit_type | LOWER |
| current_visit_date | current_visit_date | current_visit_date | to_date |
| prior_visit_date | prior_visit_date | prior_visit_date | to_date |
| _(derived)_ | | days_between_visits | datediff(current, prior) |

**Gold targets:** patient_360_master
