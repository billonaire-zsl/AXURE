#!/usr/bin/env python3
"""学生信息管理系统（命令行版）"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


DATA_FILE = Path("students.json")


@dataclass
class Student:
    student_id: str
    name: str
    age: int
    gender: str
    grade: str
    phone: str


class StudentManagementSystem:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self.students: Dict[str, Student] = {}
        self.load_data()

    def load_data(self) -> None:
        if not self.data_file.exists():
            self.students = {}
            return

        try:
            raw = json.loads(self.data_file.read_text(encoding="utf-8"))
            self.students = {
                sid: Student(**item) for sid, item in raw.items()
            }
        except (json.JSONDecodeError, TypeError, ValueError):
            print("⚠️ 数据文件格式有误，已重置为空数据库。")
            self.students = {}

    def save_data(self) -> None:
        serializable = {sid: asdict(student) for sid, student in self.students.items()}
        self.data_file.write_text(
            json.dumps(serializable, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_student(self, student: Student) -> bool:
        if student.student_id in self.students:
            return False
        self.students[student.student_id] = student
        self.save_data()
        return True

    def delete_student(self, student_id: str) -> bool:
        if student_id not in self.students:
            return False
        del self.students[student_id]
        self.save_data()
        return True

    def update_student(
        self,
        student_id: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        grade: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> bool:
        student = self.students.get(student_id)
        if not student:
            return False

        if name:
            student.name = name
        if age is not None:
            student.age = age
        if gender:
            student.gender = gender
        if grade:
            student.grade = grade
        if phone:
            student.phone = phone

        self.save_data()
        return True

    def find_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def list_students(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.student_id)


def print_student(student: Student) -> None:
    print(
        f"学号: {student.student_id} | 姓名: {student.name} | 年龄: {student.age} | "
        f"性别: {student.gender} | 班级: {student.grade} | 电话: {student.phone}"
    )


def input_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("输入不能为空，请重试。")


def input_age(prompt: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        value = input(prompt).strip()
        if allow_empty and value == "":
            return None
        if value.isdigit() and 0 < int(value) <= 120:
            return int(value)
        print("年龄需为 1-120 的数字，请重试。")


def show_menu() -> None:
    print("\n===== 学生信息管理系统 =====")
    print("1. 添加学生")
    print("2. 删除学生")
    print("3. 修改学生")
    print("4. 查询学生")
    print("5. 显示全部学生")
    print("0. 退出系统")


def run_cli() -> None:
    sms = StudentManagementSystem()

    while True:
        show_menu()
        choice = input("请选择操作: ").strip()

        if choice == "1":
            student = Student(
                student_id=input_non_empty("学号: "),
                name=input_non_empty("姓名: "),
                age=input_age("年龄: ") or 0,
                gender=input_non_empty("性别: "),
                grade=input_non_empty("班级: "),
                phone=input_non_empty("电话: "),
            )
            if sms.add_student(student):
                print("✅ 添加成功")
            else:
                print("❌ 学号已存在，添加失败")

        elif choice == "2":
            student_id = input_non_empty("请输入要删除的学号: ")
            print("✅ 删除成功" if sms.delete_student(student_id) else "❌ 未找到该学号")

        elif choice == "3":
            student_id = input_non_empty("请输入要修改的学号: ")
            student = sms.find_student(student_id)
            if not student:
                print("❌ 未找到该学号")
                continue

            print("直接回车表示不修改对应字段")
            name = input("新姓名: ").strip() or None
            age = input_age("新年龄: ", allow_empty=True)
            gender = input("新性别: ").strip() or None
            grade = input("新班级: ").strip() or None
            phone = input("新电话: ").strip() or None

            sms.update_student(student_id, name, age, gender, grade, phone)
            print("✅ 修改成功")

        elif choice == "4":
            student_id = input_non_empty("请输入要查询的学号: ")
            student = sms.find_student(student_id)
            if student:
                print_student(student)
            else:
                print("❌ 未找到该学号")

        elif choice == "5":
            students = sms.list_students()
            if not students:
                print("暂无学生信息")
            else:
                for student in students:
                    print_student(student)

        elif choice == "0":
            print("👋 已退出系统")
            break

        else:
            print("无效选项，请重新输入")


if __name__ == "__main__":
    run_cli()
