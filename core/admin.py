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
    list_display = ('patient', 'schedule', 'status', 'check_in_time', 'assigned_room', 'created_at')
    list_filter = ('status', 'schedule__date', 'schedule__doctor__department')
    search_fields = ('patient__name', 'patient__id_card')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'doctor', 'visit_time')
    search_fields = ('appointment__patient__name',)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'total_amount', 'insurance_amount', 'self_pay_amount', 'status', 'paid_at')
    list_filter = ('status', 'paid_at')
    search_fields = ('medical_record__appointment__patient__name',)
