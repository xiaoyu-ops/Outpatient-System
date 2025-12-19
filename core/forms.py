from django import forms
from .models import Department, Doctor, Schedule, Patient, Appointment, Billing


class AppointmentForm(forms.Form):
    patient_name = forms.CharField(max_length=64)
    id_card = forms.CharField(max_length=18)
    phone = forms.CharField(max_length=20)
    insurance_type = forms.ChoiceField(choices=Patient.InsuranceType.choices)
    department = forms.ModelChoiceField(queryset=Department.objects.filter(is_active=True))
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    date = forms.DateField()
    time_slot = forms.ChoiceField(choices=Schedule.TimeSlot.choices)

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        date = cleaned.get('date')
        time_slot = cleaned.get('time_slot')
        if doctor and date and time_slot:
            schedule = Schedule.objects.filter(doctor=doctor, date=date, time_slot=time_slot).first()
            if not schedule:
                raise forms.ValidationError('No schedule found for selected doctor/time.')
            cleaned['schedule'] = schedule
        return cleaned


class CheckInForm(forms.Form):
    appointment_id = forms.IntegerField()
    assigned_room = forms.CharField(max_length=16, required=False)


class BillingForm(forms.Form):
    medical_record_id = forms.IntegerField()
    total_amount = forms.DecimalField(max_digits=10, decimal_places=2)
    insurance_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    self_pay_amount = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)
    payment_method = forms.ChoiceField(choices=Billing.PaymentMethod.choices)
