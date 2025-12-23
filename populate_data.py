import os
import django
from datetime import date, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from core.models import Department, Doctor, Schedule

# 创建科室数据
departments_data = [
    {'name': '内科', 'code': 'INT', 'location': '门诊楼2层201室'},
    {'name': '外科', 'code': 'SUR', 'location': '门诊楼2层202室'},
    {'name': '儿科', 'code': 'PED', 'location': '门诊楼3层301室'},
    {'name': '妇产科', 'code': 'OBS', 'location': '门诊楼3层302室'},
    {'name': '骨科', 'code': 'ORT', 'location': '门诊楼4层401室'},
    {'name': '眼科', 'code': 'OPH', 'location': '门诊楼4层402室'},
    {'name': '耳鼻喉科', 'code': 'ENT', 'location': '门诊楼5层501室'},
    {'name': '皮肤科', 'code': 'DER', 'location': '门诊楼5层502室'},
]

# 创建医生数据
doctors_data = [
    # 内科
    {'name': '张伟', 'department_code': 'INT', 'title': 'CHIEF', 'phone': '13800001001'},
    {'name': '李娜', 'department_code': 'INT', 'title': 'ATTENDING', 'phone': '13800001002'},
    {'name': '王芳', 'department_code': 'INT', 'title': 'RESIDENT', 'phone': '13800001003'},
    # 外科
    {'name': '刘强', 'department_code': 'SUR', 'title': 'CHIEF', 'phone': '13800002001'},
    {'name': '陈静', 'department_code': 'SUR', 'title': 'ATTENDING', 'phone': '13800002002'},
    # 儿科
    {'name': '赵敏', 'department_code': 'PED', 'title': 'CHIEF', 'phone': '13800003001'},
    {'name': '孙丽', 'department_code': 'PED', 'title': 'ATTENDING', 'phone': '13800003002'},
    {'name': '周杰', 'department_code': 'PED', 'title': 'RESIDENT', 'phone': '13800003003'},
    # 妇产科
    {'name': '吴秀英', 'department_code': 'OBS', 'title': 'CHIEF', 'phone': '13800004001'},
    {'name': '郑红', 'department_code': 'OBS', 'title': 'ATTENDING', 'phone': '13800004002'},
    # 骨科
    {'name': '冯军', 'department_code': 'ORT', 'title': 'CHIEF', 'phone': '13800005001'},
    {'name': '何平', 'department_code': 'ORT', 'title': 'ATTENDING', 'phone': '13800005002'},
    # 眼科
    {'name': '朱明', 'department_code': 'OPH', 'title': 'CHIEF', 'phone': '13800006001'},
    {'name': '徐丹', 'department_code': 'OPH', 'title': 'ATTENDING', 'phone': '13800006002'},
    # 耳鼻喉科
    {'name': '马超', 'department_code': 'ENT', 'title': 'CHIEF', 'phone': '13800007001'},
    {'name': '林芳', 'department_code': 'ENT', 'title': 'RESIDENT', 'phone': '13800007002'},
    # 皮肤科
    {'name': '胡磊', 'department_code': 'DER', 'title': 'ATTENDING', 'phone': '13800008001'},
    {'name': '梁慧', 'department_code': 'DER', 'title': 'RESIDENT', 'phone': '13800008002'},
]

def populate_departments():
    print("创建科室数据...")
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults={
                'name': dept_data['name'],
                'location': dept_data['location'],
                'is_active': True
            }
        )
        if created:
            print(f"✓ 创建科室: {dept.name}")
        else:
            print(f"- 科室已存在: {dept.name}")

def populate_doctors():
    print("\n创建医生数据...")
    for doc_data in doctors_data:
        department = Department.objects.get(code=doc_data['department_code'])
        doc, created = Doctor.objects.get_or_create(
            phone=doc_data['phone'],
            defaults={
                'name': doc_data['name'],
                'department': department,
                'title': doc_data['title'],
                'available_slots_per_day': 20
            }
        )
        if created:
            print(f"✓ 创建医生: {doc.name} - {department.name} ({doc.get_title_display()})")
        else:
            print(f"- 医生已存在: {doc.name}")

def populate_schedules():
    print("\n创建排班数据（未来7天）...")
    today = date.today()
    doctors = Doctor.objects.all()
    
    for i in range(7):  # 未来7天
        schedule_date = today + timedelta(days=i)
        for doctor in doctors:
            # 为每个医生创建上午和下午的排班
            for time_slot in ['AM', 'PM']:
                schedule, created = Schedule.objects.get_or_create(
                    doctor=doctor,
                    date=schedule_date,
                    time_slot=time_slot,
                    defaults={
                        'room_no': f"{doctor.department.code}-{doctor.id}",
                        'capacity': 20,
                        'status': 'OPEN'
                    }
                )
                if created:
                    print(f"✓ 创建排班: {schedule_date} {time_slot} - {doctor.name}")

if __name__ == '__main__':
    print("=" * 50)
    print("开始填充数据...")
    print("=" * 50)
    
    populate_departments()
    populate_doctors()
    populate_schedules()
    
    print("\n" + "=" * 50)
    print("数据填充完成！")
    print("=" * 50)
    print(f"科室总数: {Department.objects.count()}")
    print(f"医生总数: {Doctor.objects.count()}")
    print(f"排班总数: {Schedule.objects.count()}")
