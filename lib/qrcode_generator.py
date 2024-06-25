from tkinter import messagebox
import segno
import io
import os

# from threading import Event
import tkinter as tk
from svglib.svglib import svg2rlg
from reportlab.pdfgen import canvas
import timeit

basedir = os.getcwd()


def read_file(file_name: str) -> list:
    with open(file_name, 'r') as file:
        lines = file.readlines()

    return lines


def find_biggest_version(codes: list, progress_var: tk.IntVar) -> int:
    codes_size = len(codes)
    biggest_version = 0
    for i, code in enumerate(codes):
        progress_var.set(int((i + 1) / codes_size * 100))
        version = segno.make(code.strip(), micro=False, error='M').version
        if version > biggest_version:
            biggest_version = version

    return biggest_version


def check_file_not_exist(file_name: str) -> bool:
    if os.path.exists(file_name):
        if messagebox.askyesno("Arquivo já existe", "Deseja sobrescrever o arquivo?"):
            return True
        else:
            return False

    return True


def create_qrcode_pdf(codes: list, file_name: str, version: int, progress_var: tk.IntVar) -> str:
    file_path = os.path.dirname(file_name)
    file_name = os.path.basename(file_name)[:-4]
    file_name = file_path + f'/{file_name}_v{version}.pdf'
    if check_file_not_exist(file_name):
        codes_size = len(codes)
        size = 25 + 4 * version
        relatorio = canvas.Canvas(
            file_name,
            pagesize=(size, size),
        )
        for i, code in enumerate(codes):
            progress_var.set(int((i + 1) / codes_size * 100))
            qrcode = segno.make(code.strip(), micro=False, error='M', version=version)
            buff = io.BytesIO()
            qrcode.save(buff, kind='svg', scale=1)
            buff.seek(0)
            drawing = svg2rlg(buff)
            drawing.drawOn(relatorio, 0, 0)
            relatorio.setFontSize(1)
            relatorio.drawString(1, 1, code[:-1].strip())
            relatorio.showPage()
        relatorio.save()

        return file_name

    return None


def main():
    file_name = input('Digite o nome do arquivo: ')
    codes = read_file(file_name)
    biggest_version = find_biggest_version(codes)
    pdf_time = timeit.timeit(lambda: create_qrcode_pdf(codes, file_name, biggest_version), number=1)
    print(f'tempo de execução: {pdf_time}')


if __name__ == '__main__':
    main()
