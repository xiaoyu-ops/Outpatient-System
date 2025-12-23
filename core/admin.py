from django.contrib import admin
from django.db.models import Count

from .models import Department, Doctor, Patient, Schedule, Appointment, MedicalRecord, Billing


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'title', 'phone', 'available_slots_per_day')
    list_filter = ('department', 'title')
    search_fields = ('name', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(future_schedules=Count('schedules'))


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_card', 'phone', 'insurance_type')
    search_fields = ('name', 'id_card', 'phone')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'time_slot', 'room_no', 'capacity', 'status', 'booked_count')
    list_filter = ('date', 'time_slot', 'status', 'doctor__department')
    search_fields = ('doctor__name', 'room_no')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(appt_count=Count('appointments'))

    def booked_count(self, obj):
        return obj.appt_count


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_appointment_id', 'patient', 'schedule', 'status', 'get_medical_record_id', 'check_in_time', 'created_at')
    list_filter = ('status', 'schedule__date', 'schedule__doctor__department')
    search_fields = ('patient__name', 'patient__id_card', 'id')
    readonly_fields = ('get_medical_record_id',)
    
    def get_appointment_id(self, obj):
        return f"预约单号: {obj.id}"
    get_appointment_id.short_description = '预约单号'
    
    def get_medical_record_id(self, obj):
        try:
            return f"就诊单号: {obj.medical_record.id}"
        except MedicalRecord.DoesNotExist:
            return "未生成就诊单"
    get_medical_record_id.short_description = '就诊单号'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_record_id', 'get_patient_name', 'doctor', 'get_department', 'diagnosis', 'visit_time')
    search_fields = ('appointment__patient__name', 'id', 'appointment__patient__id_card')
    list_filter = ('doctor__department', 'visit_time')
    readonly_fields = ('get_record_id', 'get_patient_name', 'get_appointment_id')
    
    def get_record_id(self, obj):
        return f"就诊单号: {obj.id}"
    get_record_id.short_description = '就诊单号'
    
    def get_patient_name(self, obj):
        return obj.appointment.patient.name
    get_patient_name.short_description = '患者姓名'
    
    def get_department(self, obj):
        return obj.doctor.department.name
    get_department.short_description = '科室'
    
    def get_appointment_id(self, obj):
        return f"预约单号: {obj.appointment.id}"
    get_appointment_id.short_description = '预约单号'


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('get_record_id', 'get_patient_name', 'total_amount', 'insurance_amount', 'self_pay_amount', 'status', 'payment_method', 'paid_at')
    list_filter = ('status', 'payment_method', 'paid_at')
    search_fields = ('medical_record__appointment__patient__name', 'medical_record__id')
    readonly_fields = ('get_record_id', 'get_patient_name', 'get_doctor')
    
    def get_record_id(self, obj):
        return f"就诊单号: {obj.medical_record.id}"
    get_record_id.short_description = '就诊单号'
    
    def get_patient_name(self, obj):
        return obj.medical_record.appointment.patient.name
    get_patient_name.short_description = '患者姓名'
    
    def get_doctor(self, obj):
        return obj.medical_record.doctor.name
    get_doctor.short_description = '医生'
