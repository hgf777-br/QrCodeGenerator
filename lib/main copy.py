import os
from threading import Thread, Event
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import (
    SUCCESS,
    OUTLINE,
    INFO,
    DETERMINATE,
    STRIPED,
    DANGER,
    WARNING,
    LINK,
)
from qrcode_generator import read_file, find_biggest_version, create_qrcode_pdf
# from time import sleep

basedir = os.path.dirname(__file__)


class GerarQRCode:
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window and its components.

        Parameters:
        root (tk.Tk): The root window object.

        Returns:
        None
        """
        root.title('Gerador de QRCode')
        root.iconbitmap(os.path.join(basedir, '..\\images\\favicon.ico'))
        # root.geometry("800x400")
        root.minsize(800, 300)
        root.resizable(True, False)
        root.grid_columnconfigure(1, weight=1, minsize=500)
        root.grid_rowconfigure(1, weight=1)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        check_file_wrapper = (root.register(self.check_file), '%P')

        self.frame = ttk.Frame(master=root)
        self.label_file_explorer = ttk.Label(
            master=self.frame,
            text="Escolha o arquivo com os códigos",
            padding=(10, 20, 10, 10),
            font=("TkHeadingFont", 12, 'bold'),
        )
        self.file_name = tk.StringVar()
        self.entry_file_explorer = ttk.Entry(
            master=self.frame,
            justify='left',
            textvariable=self.file_name,
            validate='focusout',
            validatecommand=check_file_wrapper,
        )
        self.button_explore = ttk.Button(
            master=self.frame,
            text="Procurar arquivo",
            command=self.browse_files,
            bootstyle=(INFO, OUTLINE),
        )
        self.error = tk.StringVar()
        self.error_file_explorer = ttk.Label(
            master=self.frame,
            textvariable=self.error,
            font=("TkCaptionFont", 8),
            bootstyle=(DANGER),
        )
        self.button_generate_qrcode = ttk.Button(
            master=self.frame,
            text="Gerar QRCode",
            command=self.initialize_qrcode_generator,
            bootstyle=(SUCCESS, OUTLINE),
        )
        self.label_status = ttk.Label(
            master=self.frame,
            text="Aguardando arquivo para processar",
            padding=10,
            font=("TkSmallCaptionFont"),
            bootstyle=(WARNING),
        )
        self.progress_value = tk.IntVar()
        self.status_progressbar = ttk.Progressbar(
            master=self.frame,
            orient=tk.HORIZONTAL,
            mode=DETERMINATE,
            bootstyle=(STRIPED, SUCCESS),
            variable=self.progress_value,
        )
        self.link_pdf = ttk.Button(
            master=self.frame,
            text="",
            command=self.open_pdf,
            bootstyle=(INFO, LINK),
        )

        self.frame.grid(column=1, row=1, sticky=(tk.W, tk.N, tk.S, tk.E))
        self.frame.columnconfigure(2, weight=1, minsize=500)

        self.label_file_explorer.grid(column=1, row=1, sticky=tk.W, columnspan=2)
        self.button_explore.grid(column=1, row=2, padx=(10, 0), sticky=tk.W)
        self.entry_file_explorer.grid(column=2, row=2, padx=(0, 10), sticky=tk.EW)
        self.button_generate_qrcode.grid(column=1, row=4, padx=(10, 0), pady=(20, 0), sticky=tk.EW)
        self.label_status.grid(column=1, row=5, sticky=tk.W, columnspan=2)
        self.status_progressbar.grid(
            column=1, row=6, padx=10, pady=(0, 10), sticky=tk.EW, columnspan=2
        )

    def check_file(self, filename: str) -> bool:
        """
        Check if the given file exists. If it does, enable the 'Gerar QRCode' button.

        Parameters:
        filename (str): The path of the file to be checked.

        Returns:
        bool: True if the file exists, False otherwise.
        """
        if os.path.isfile(filename):
            # Enable the 'Gerar QRCode' button if the file exists
            self.button_generate_qrcode.config(state='!disabled')
            return True
        else:
            # Disable the 'Gerar QRCode' button if the file does not exist
            self.button_generate_qrcode.config(state='disabled')
            return False

    def open_pdf(self) -> None:
        """
        Open the generated PDF file using the default system application.

        This method retrieves the file path from the 'text' attribute of the 'link_pdf' button
        and uses the 'os.system' function to open the file.

        Parameters:
        None

        Returns:
        None
        """
        os.system(self.link_pdf.cget('text'))

    def browse_files(self) -> None:
        """
        Open a file dialog to select a text file containing codes.
        Update the entry widget with the selected file path and disable the 'Gerar QRCode' button.

        Parameters:
        None

        Returns:
        None
        """
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Escolha o arquivo com os códigos",
            filetypes=(("Text files", "*.txt*"), ("all files", "*.*")),
        )

        # Validate if file exists
        # if os.path.isfile(filename):
        #     self.error.set('tudo ok com o arquivo')
        #     self.error_file_explorer.grid(
        #         column=1, row=3, padx=10, pady=(3, 0), sticky=EW, columnspan=2
        #     )

        self.entry_file_explorer.state(['!invalid'])
        self.button_generate_qrcode.config(state='!disabled')
        self.file_name.set(filename)

    def initialize_qrcode_generator(self) -> None:
        if self.entry_file_explorer.get() != '':
            self.button_generate_qrcode.config(state='disabled')
            self.link_pdf.grid_forget()
            self.thread_event = Event()
            self.qr_thread = Thread(target=self.qrcode_generator, args=(self.thread_event,)).start()

    def qrcode_generator(self, event: Event) -> None:
        # sleep(1)
        # for i in range(101):
        #     if event.is_set():
        #         break
        #     sleep(0.01)
        #     self.progress_value.set(i)
        #     print(self.progress_value.get())

        # for i in range(101):
        #     if event.is_set():
        #         break
        #     sleep(0.01)
        #     self.progress_value.set(i)
        #     print(self.progress_value.get())

        self.label_status.config(bootstyle=(INFO))
        self.label_status.config(text='Iniciando...')
        file_name = self.entry_file_explorer.get()
        codes = read_file(file_name)

        self.label_status.config(text='Analisando os códigos')
        version = find_biggest_version(codes, self.progress_value)

        self.label_status.config(text='Gerando os QRCodes')
        file_name = create_qrcode_pdf(codes, file_name, version, self.progress_value)

        self.label_status.config(bootstyle=(SUCCESS))
        self.label_status.config(text='Códigos Gerados com sucesso!')
        self.button_generate_qrcode.config(state='!disabled')
        self.link_pdf.config(text=file_name)
        self.link_pdf.grid(column=1, row=7, sticky=tk.W, columnspan=2)

        return

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja mesmo sair?"):
            # self.thread_event.set()
            # self.qr_thread.join()
            root.destroy()


if __name__ == '__main__':
    root = ttk.Window(themename='darkly')
    app = GerarQRCode(root)
    root.mainloop()
