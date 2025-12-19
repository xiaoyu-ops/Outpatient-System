from django import forms
from .models import Department, Doctor, Schedule, Patient, Appointment, Billing

class BootstrapFormMixin:
    """Mixin to add Bootstrap classes to form fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget_class = field.widget.attrs.get('class', '')
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = f'{widget_class} form-check-input'
            else:
                field.widget.attrs['class'] = f'{widget_class} form-control'

class AppointmentForm(BootstrapFormMixin, forms.Form):
    patient_name = forms.CharField(label="患者姓名", max_length=64)
    id_card = forms.CharField(label="身份证号", max_length=18)
    phone = forms.CharField(label="手机号码", max_length=20)
    insurance_type = forms.ChoiceField(label="医保类型", choices=Patient.InsuranceType.choices)
    department = forms.ModelChoiceField(label="选择科室", queryset=Department.objects.filter(is_active=True))
    doctor = forms.ModelChoiceField(label="选择医生", queryset=Doctor.objects.all())
    date = forms.DateField(label="就诊日期", widget=forms.DateInput(attrs={'type': 'date'}))
    time_slot = forms.ChoiceField(label="就诊时段", choices=Schedule.TimeSlot.choices)

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        date = cleaned.get('date')
        time_slot = cleaned.get('time_slot')
        department = cleaned.get('department')

        if doctor and department and doctor.department_id != department.id:
            raise forms.ValidationError('该医生不属于所选科室，请重新选择。')

        if doctor and date and time_slot:
            schedule = Schedule.objects.filter(doctor=doctor, date=date, time_slot=time_slot).first()
            if not schedule:
                raise forms.ValidationError('所选医生在该时段无排班。')
            cleaned['schedule'] = schedule
        return cleaned

class CheckInForm(BootstrapFormMixin, forms.Form):
    appointment_id = forms.IntegerField(label="预约编号", required=False, widget=forms.NumberInput(attrs={'placeholder': '请输入预约ID'}))
    id_card = forms.CharField(label="身份证号", required=False, max_length=18, widget=forms.TextInput(attrs={'placeholder': '或输入身份证号查找'}))
    phone = forms.CharField(label="手机号码", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder': '或输入手机号查找'}))
    assigned_room = forms.CharField(label="分配诊室", max_length=16, required=False, help_text="留空则使用排班默认诊室")

    def clean(self):
        cleaned = super().clean()
        appointment_id = cleaned.get('appointment_id')
        id_card = cleaned.get('id_card')
        phone = cleaned.get('phone')

        if not any([appointment_id, id_card, phone]):
            raise forms.ValidationError('请至少提供一项：预约编号、身份证号或手机号。')

        qs = Appointment.objects.select_related('schedule')
        appointment = None
        
        if appointment_id:
            appointment = qs.filter(pk=appointment_id).first()
            if not appointment:
                raise forms.ValidationError('未找到该编号的预约记录。')
        else:
            filters = {}
            if id_card:
                filters['patient__id_card'] = id_card
            if phone:
                filters['patient__phone'] = phone
            # 优先查找最近的 BOOKED 状态预约
            appointment = qs.filter(status=Appointment.Status.BOOKED, **filters).order_by('-created_at').first()
            if not appointment:
                raise forms.ValidationError('未找到该患者的待就诊预约。')

        if appointment.status != Appointment.Status.BOOKED:
            raise forms.ValidationError(f'该预约状态为“{appointment.get_status_display()}”，无法进行报到登记。')

        cleaned['appointment'] = appointment
        return cleaned

class BillingForm(BootstrapFormMixin, forms.Form):
    medical_record_id = forms.IntegerField(label="就诊记录ID", widget=forms.HiddenInput())
    total_amount = forms.DecimalField(label="应收总额 (元)", max_digits=10, decimal_places=2)
    insurance_amount = forms.DecimalField(label="医保统筹 (元)", max_digits=10, decimal_places=2, initial=0)
    self_pay_amount = forms.DecimalField(label="个人自费 (元)", max_digits=10, decimal_places=2, initial=0)
    payment_method = forms.ChoiceField(label="支付方式", choices=Billing.PaymentMethod.choices)

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get('total_amount')
        insurance = cleaned.get('insurance_amount')
        self_pay = cleaned.get('self_pay_amount')

        if None not in (total, insurance, self_pay):
            if abs(total - (insurance + self_pay)) > 0.01:
                raise forms.ValidationError('金额不平：应收总额必须等于医保统筹与个人自费之和。')
        return cleaned
