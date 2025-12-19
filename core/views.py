from datetime import datetime
from django.db import transaction
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseBadRequest

from .forms import AppointmentForm, CheckInForm, BillingForm
from .models import (
    Appointment,
    Billing,
    MedicalRecord,
    Patient,
    Schedule,
)


def appointment_booking(request):
    message = None
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                patient, _ = Patient.objects.get_or_create(
                    id_card=form.cleaned_data['id_card'],
                    defaults={
                        'name': form.cleaned_data['patient_name'],
                        'phone': form.cleaned_data['phone'],
                        'insurance_type': form.cleaned_data['insurance_type'],
                    },
                )
                schedule = Schedule.objects.select_for_update().get(pk=form.cleaned_data['schedule'].pk)

                if schedule.status == Schedule.Status.CLOSED:
                    return HttpResponseBadRequest('该排班已关闭。')

                booked = schedule.appointments.filter(status=Appointment.Status.BOOKED).count()
                if booked >= schedule.capacity or schedule.status == Schedule.Status.FULL:
                    return HttpResponseBadRequest('该排班已满。')

                appointment, created = Appointment.objects.get_or_create(
                    patient=patient,
                    schedule=schedule,
                    defaults={'status': Appointment.Status.BOOKED},
                )
                if not created:
                    message = '该患者已预约此时段。'
                else:
                    if booked + 1 >= schedule.capacity:
                        schedule.status = Schedule.Status.FULL
                        schedule.save(update_fields=['status'])
                    message = '预约成功。'
    else:
        form = AppointmentForm()
    return render(request, 'core/appointment_booking.html', {'form': form, 'message': message})


def check_in(request):
    message = None
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                appointment = Appointment.objects.select_for_update().select_related('schedule__doctor').get(
                    pk=form.cleaned_data['appointment'].pk
                )
                if appointment.status != Appointment.Status.BOOKED:
                    return HttpResponseBadRequest('该预约不在待登记状态。')
                appointment.status = Appointment.Status.COMPLETED
                appointment.check_in_time = timezone.now()
                appointment.assigned_room = form.cleaned_data.get('assigned_room') or appointment.schedule.room_no
                appointment.save(update_fields=['status', 'check_in_time', 'assigned_room'])

                MedicalRecord.objects.get_or_create(
                    appointment=appointment,
                    defaults={'doctor': appointment.schedule.doctor},
                )
                message = '登记完成，已生成就诊记录。'
    else:
        form = CheckInForm()
    return render(request, 'core/check_in.html', {'form': form, 'message': message})


def billing(request):
    message = None
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                medical_record = MedicalRecord.objects.select_for_update().select_related('appointment').get(
                    pk=form.cleaned_data['medical_record_id']
                )
                if medical_record.appointment.status != Appointment.Status.COMPLETED:
                    return HttpResponseBadRequest('该预约尚未完成就诊，无法结算。')
                billing_obj, created = Billing.objects.select_for_update().get_or_create(
                    medical_record=medical_record,
                    defaults={
                        'total_amount': form.cleaned_data['total_amount'],
                        'insurance_amount': form.cleaned_data['insurance_amount'],
                        'self_pay_amount': form.cleaned_data['self_pay_amount'],
                        'payment_method': form.cleaned_data['payment_method'],
                        'status': Billing.Status.PAID,
                        'paid_at': timezone.now(),
                    },
                )
                if not created:
                    if billing_obj.status == Billing.Status.PAID:
                        return HttpResponseBadRequest('该记录已结算，无需重复支付。')
                    billing_obj.total_amount = form.cleaned_data['total_amount']
                    billing_obj.insurance_amount = form.cleaned_data['insurance_amount']
                    billing_obj.self_pay_amount = form.cleaned_data['self_pay_amount']
                    billing_obj.payment_method = form.cleaned_data['payment_method']
                    billing_obj.status = Billing.Status.PAID
                    billing_obj.paid_at = timezone.now()
                    billing_obj.save()
                medical_record.appointment.status = Appointment.Status.PAID
                medical_record.appointment.save(update_fields=['status'])
                message = '结算完成，患者可离院。'
    else:
        form = BillingForm()
    return render(request, 'core/billing.html', {'form': form, 'message': message})


def stats_view(request):
    qs = (
        Billing.objects.filter(status=Billing.Status.PAID)
        .annotate(stat_date=TruncDate('paid_at'))
        .values('stat_date', dept_name=F('medical_record__doctor__department__name'))
        .annotate(revenue=Sum('total_amount'), visits=Count('medical_record'))
        .order_by('-stat_date', 'dept_name')
    )
    return render(request, 'core/stats.html', {'rows': qs})
