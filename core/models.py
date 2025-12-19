from django.db import models
from django.db.models import Q, F


class Department(models.Model):
    name = models.CharField(max_length=64, unique=True)
    code = models.CharField(max_length=16, unique=True)
    location = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self) -> str:
        return f"{self.name}"


class Doctor(models.Model):
    class Title(models.TextChoices):
        RESIDENT = 'RESIDENT', 'Resident'
        ATTENDING = 'ATTENDING', 'Attending'
        CHIEF = 'CHIEF', 'Chief Physician'

    name = models.CharField(max_length=64)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='doctors')
    title = models.CharField(max_length=16, choices=Title.choices, default=Title.RESIDENT)
    phone = models.CharField(max_length=20, unique=True)
    available_slots_per_day = models.PositiveIntegerField(default=20)

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        unique_together = ('name', 'department')

    def __str__(self) -> str:
        return f"{self.name} ({self.department.name})"


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class InsuranceType(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'
        SELF_PAY = 'SELF', 'Self Pay'

    name = models.CharField(max_length=64)
    id_card = models.CharField(max_length=18, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    insurance_type = models.CharField(max_length=8, choices=InsuranceType.choices, default=InsuranceType.PUBLIC)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self) -> str:
        return f"{self.name} ({self.id_card})"


class Schedule(models.Model):
    class TimeSlot(models.TextChoices):
        MORNING = 'AM', 'Morning'
        AFTERNOON = 'PM', 'Afternoon'
        EVENING = 'EV', 'Evening'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        FULL = 'FULL', 'Full'
        CLOSED = 'CLOSED', 'Closed'

    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='schedules')
    date = models.DateField()
    time_slot = models.CharField(max_length=2, choices=TimeSlot.choices)
    room_no = models.CharField(max_length=16, blank=True)
    capacity = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.OPEN)

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        unique_together = ('doctor', 'date', 'time_slot')
        constraints = [
            models.CheckConstraint(check=Q(capacity__gte=1), name='schedule_capacity_positive'),
        ]

    def __str__(self) -> str:
        return f"{self.date} {self.get_time_slot_display()} - {self.doctor.name}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'BOOKED', 'Booked'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No Show'

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.BOOKED)
    check_in_time = models.DateTimeField(null=True, blank=True)
    assigned_room = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        unique_together = ('patient', 'schedule')

    def __str__(self) -> str:
        return f"{self.patient.name} @ {self.schedule}"


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.PROTECT, related_name='medical_record')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='medical_records')
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    visit_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'

    def __str__(self) -> str:
        return f"Record {self.appointment_id}"


class Billing(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        REFUNDED = 'REFUNDED', 'Refunded'

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Card'
        INSURANCE = 'INSURANCE', 'Insurance Direct'

    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, related_name='billing')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    self_pay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=16, choices=PaymentMethod.choices, blank=True)

    class Meta:
        verbose_name = 'Billing'
        verbose_name_plural = 'Billings'
        constraints = [
            models.CheckConstraint(
                check=(Q(total_amount__gte=0) & Q(insurance_amount__gte=0) & Q(self_pay_amount__gte=0)),
                name='billing_amount_non_negative',
            ),
            models.CheckConstraint(
                check=Q(total_amount=F('insurance_amount') + F('self_pay_amount')),
                name='billing_amount_consistency',
            ),
        ]

    def __str__(self) -> str:
        return f"Billing for record {self.medical_record_id}: {self.total_amount}"
