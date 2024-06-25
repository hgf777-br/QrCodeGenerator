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
    LIGHT,
)
from lib.qrcode_generator import read_file, find_biggest_version, create_qrcode_pdf

BASEDIR = os.path.dirname(__file__)
THEME = 'superhero'


class GerarQRCode:
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window and its components.

        Parameters:
        root (tk.Tk): The root window object.

        Returns:
        None
        """
        root.title('Gerador de QrCode')
        root.iconbitmap(os.path.join(BASEDIR, '.\\images\\favicon.ico'))
        root.minsize(800, 270)
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
        self.use_labels = tk.BooleanVar()
        self.button_use_labels = ttk.Checkbutton(
            master=self.frame,
            text="aplicar legenda",
            variable=self.use_labels,
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
            bootstyle=(LIGHT, LINK),
        )

        self.frame.grid(column=1, row=1, sticky=(tk.W, tk.N, tk.S, tk.E))
        self.frame.columnconfigure(2, weight=1, minsize=500)

        self.label_file_explorer.grid(column=1, row=1, sticky=tk.W, columnspan=2)
        self.button_explore.grid(column=1, row=2, padx=(10, 0), sticky=tk.W)
        self.entry_file_explorer.grid(column=2, row=2, padx=(0, 10), sticky=tk.EW)
        self.button_generate_qrcode.grid(column=1, row=4, padx=(10, 0), pady=(20, 0), sticky=tk.EW)
        self.button_use_labels.grid(column=2, row=4, padx=(10, 0), pady=(20, 0), sticky=tk.EW)
        self.label_status.grid(column=1, row=5, sticky=tk.W, columnspan=2)
        self.status_progressbar.grid(column=1, row=6, padx=10, sticky=tk.EW, columnspan=2)

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
        os.startfile(self.link_pdf.cget('text'))

    def browse_files(self) -> None:
        """
        Open a file dialog to select a text file containing codes.
        Update the entry widget with the selected file path and disable the 'Gerar QRCode' button.

        Parameters:
        None

        Returns:
        None
        """
        entry_path = self.entry_file_explorer.get()
        initial_dir: str = '.' if entry_path == '' else os.path.dirname(entry_path)
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Escolha o arquivo com os códigos",
            filetypes=(("Text files", "*.txt*"), ("all files", "*.*")),
        )
        self.entry_file_explorer.state(['!invalid'])
        self.button_generate_qrcode.config(state='!disabled')
        if filename != '':
            self.file_name.set(filename)

    def initialize_qrcode_generator(self) -> None:
        if self.entry_file_explorer.get() != '':
            # Disable the 'Gerar QRCode' button
            self.button_generate_qrcode.config(state='disabled')
            # Hide the link_pdf button
            self.link_pdf.grid_forget()
            # Create an event object for thread synchronization
            self.thread_event = Event()
            # Start a new thread to execute the qrcode_generator method
            self.qr_thread = Thread(target=self.qrcode_generator, args=(self.thread_event,)).start()

    def qrcode_generator(self, event: Event) -> None:
        """
        This method is responsible for generating QR codes from the provided codes.
        It updates the GUI with the progress status and generates
        a PDF file containing the QR codes.

        Parameters:
        event (Event): An event object that can be used to stop the thread execution.
        Returns:
        None
        """

        # Update the status label to 'Iniciando...'
        self.label_status.config(bootstyle=(INFO))
        self.label_status.config(text='Iniciando...')
        # Get the file name from the entry widget
        file_name = self.entry_file_explorer.get()
        # Read the codes from the file
        codes = read_file(file_name)
        # Update the status label to 'Analisando os códigos'
        self.label_status.config(text='Analisando os códigos')
        # Find the biggest QR code version that can fit all the codes
        version = find_biggest_version(codes, self.progress_value)
        # Update the status label to 'Gerando os QRCodes'
        self.label_status.config(text='Gerando os QRCodes')
        # Generate a PDF file containing all the QR codes
        file_name = create_qrcode_pdf(
            codes,
            file_name,
            version,
            self.progress_value,
            self.use_labels.get(),
        )
        if file_name is not None:
            # Update the status label to 'Códigos gerados com sucesso!'
            self.label_status.config(bootstyle=(SUCCESS))
            self.label_status.config(text='Códigos gerados com sucesso!')
            # Configure the link_pdf button with the generated PDF file name
            self.link_pdf.config(text=file_name)
            # Display the link_pdf button
            self.link_pdf.grid(column=1, row=7, sticky=tk.W, columnspan=2)
        else:
            # Update the status label to 'Códigos não gerados...'
            self.label_status.config(bootstyle=(DANGER))
            self.label_status.config(text='Códigos não gerados...')

        # Enable the 'Gerar QRCode' button
        self.button_generate_qrcode.config(state='!disabled')
        self.progress_value.set(0)

    def on_closing(self):
        if messagebox.askyesno("Sair", "Deseja mesmo sair?"):
            # self.thread_event.set()
            # self.qr_thread.join()
            root.destroy()


if __name__ == '__main__':
    root = ttk.Window(themename=THEME)
    app = GerarQRCode(root)
    root.mainloop()
