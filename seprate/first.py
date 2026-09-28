# def student_management_system():
#     students = []

#     def add_student(name, age, email, phone_number):
#         student = { 'name' : name,
#                     'age' : age,
#                     'email': email,
#                     'phone_number': phone_number
#                   }
#     students.append(student)
#     print(f"Student {name} added successfully.")
#     def view_students():
#         if not students:
#             print("No students found.")
#             return
#         for student in students:
#             print(f"Name: {student['name']}, Age: {student['age']}, email: {student['email']}, phone-number:{student['phone_numnber']}")

#     def remove_student(name):
#         nonlocal students
#         students = [student for student in students if student['name'] != name],
#         students =[student for student in students if student['email']!= email],
#         students =[student for student in students if student['phone_number']!= phone_number]

#         print(f"student{name} name removed succesfully")

#         while True:
#             print("\nStudent Management System")
#             print("1. Add Student")
#             print("2. view students")
#             print("3. remove students")

#             choice = input("Enter your choice: ")

#             if choice == '1':
#                 name = input("Enter student's name: ")
#                 age = int(input("Enter student's age: "))
#                 email = (input("enter student's email"))
#                 phone_number = int(input("Enter student's phone_number"))
#                 add_student(name, age, email, phone_number)

#             elif choice == '2':
#                 view_students()
#             elif choice == '3':
#                 name = input("Enter student's name to remove: ")
#                 remove_student(name)
#             elif choice == '4':
#                 print("Exiting the system.")
#                 break
#             else:
#                 print("Invalid choice. Please try a again")