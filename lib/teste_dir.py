import os

print(os.getcwd())

pdf = os.path.join(os.getcwd(), 'pdf')

print(pdf)

print(os.path.isdir(pdf))
if not os.path.isdir(pdf):
    os.mkdir(pdf)

print(os.path.isdir(pdf))
