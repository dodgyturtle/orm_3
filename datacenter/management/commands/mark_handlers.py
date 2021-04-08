import sys
from random import choice

from datacenter.models import (
    Chastisement,
    Commendation,
    Lesson,
    Mark,
    Schoolkid,
    Subject,
)
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from environs import Env

env = Env()
env.read_env()


class Command(BaseCommand):
    help = "Fix marks. Delete chastisements. Create commendation."

    def handle(self, *args, **options):
        main()


def load_student(name):
    student = Schoolkid.objects.get(full_name__contains=name)
    return student


def fix_marks(schoolkid):
    points = [4, 5]
    marks = Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3])
    for mark in marks:
        mark.points = choice(points)
        mark.save()


def remove_chastisements(schoolkid):
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    chastisements.delete()


def create_commendation(student, commendation_texts, subject_title):
    subject = Subject.objects.get(
        title=subject_title, year_of_study=student.year_of_study
    )
    lesson = (
        Lesson.objects.filter(
            year_of_study=student.year_of_study,
            group_letter=student.group_letter,
            subject=subject,
        )
        .order_by("-date")
        .first()
    )
    commendation_date = lesson.date
    commendation_teacher = lesson.teacher
    Commendation.objects.create(
        subject=subject,
        teacher=commendation_teacher,
        created=commendation_date,
        schoolkid=student,
        text=choice(commendation_texts),
    )


def main():
    commendation_texts = [
        "Молодец!",
        "Отлично!",
        "Замечательно!",
        "Прекрасное начало!",
        "Так держать!",
        "Ты на верном пути!",
        "Здорово!",
        "Это как раз то, что нужно!",
        "Я тобой горжусь!",
        "С каждым разом у тебя получается всё лучше!",
        "Мы с тобой не зря поработали!",
        "Я вижу, как ты стараешься!",
        "Ты растешь над собой!",
        "Ты многое сделал, я это вижу!",
        "Теперь у тебя точно все получится!",
    ]
    try:
        student_name = env("STUDENT_NAME")
        subject_title = env("SUBJECT_TITLE")
    except environs.EnvError:
        print("В конфигурационном файле '.env' не указана ФИО ученика и/или предмет.")
        sys.exit(1)
    try:
        student = load_student(student_name)
    except MultipleObjectsReturned:
        print(f"Найдено больше одного совпадения с именем ФИО: {student_name}.")
        sys.exit(1)
    except ObjectDoesNotExist:
        print(f"Ученика {student_name} не найдено.")
        sys.exit(1)
    fix_marks(student)
    remove_chastisements(student)
    create_commendation(student, commendation_texts, subject_title)
