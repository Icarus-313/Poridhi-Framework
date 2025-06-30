# def hell():
#     return "hello Adil!"
# def add(x, y):
#     return x+y
# def route(path):
#     if path == "/" :
#         return hell()
#     elif path == "add":
#         return add(3,4)
#     else:
#         return "You are a good person!"
    
# print(route("/"))
# print(route("add"))
# print(route(""))

# x=0
# while True: 
#     x+=1
#     if x==17:
#       continue
#     if x%3==0:
#       continue 
#     if x>21:
#       break
#     print(x)
# numbers = [2, 5, 8, 11, 14, 17]
# i=0
# while True:
#     num = numbers[i]
#     if num%2 ==0 : 
#         numbers.remove(numbers[i])
#         i += 1
#     if i==3 :
#        break
    
    
# class Rectangle:
#    def __init__(self, width, height):
#          self.width = width
#          self.height = height

#    def area(self):
#             return self.width * self.height

# are = Rectangle(5,10) 
# print(are.area())

# class Student:
#     def __init__(self, name, id, marks):
#         self.name = name
#         self.id = id
#         self.marks = marks
#     def average(self):
#         return sum(self.marks)/len(self.marks)
    
#     def is_passed(self):
#         return self.average() >=40
    
# s = Student("Adil", 123, [70, 65, 50, 40])
# print(s.average())     # 56.25
# print(s.is_passed())   # True




# def safe_run(func):
#     def wrapper(*args, **kwargs):
#      print(f"Output:\nRunning...\n")
#      func(*args, **kwargs)
#      print(f"Done!\n")

#     return wrapper


# @safe_run
# def divide(a, b):
#     print (a / b)
# a = int(input())
# b = int(input("Enter second number: "))

# divide(a,b)

text = "Hello"
binary = b"Hello"

print(type(text))   # <class 'str'>
print(type(binary)) # <class 'bytes'>