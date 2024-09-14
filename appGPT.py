import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from artoria import display
from pendragon import Grading

ANSWER_KEYS = ['A'] * 50
NUM_QUESTIONS = 50

class GradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Chấm Điểm")

        # Khung bên trái để chứa các nút và thông tin
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Khung bên phải để hiển thị hình ảnh
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Nút chọn file ảnh
        self.upload_button = tk.Button(self.left_frame, text="Chọn Ảnh", command=self.upload_image)
        self.upload_button.pack(pady=10)

        # Nút chấm điểm
        self.grade_button = tk.Button(self.left_frame, text="Chấm Điểm", command=self.grade_image, state=tk.DISABLED)
        self.grade_button.pack(pady=10)

        # Thông tin mã thí sinh, mã đề thi, điểm số
        self.info_label = tk.Label(self.left_frame, text="Mã thí sinh: \nMã đề thi: \nĐiểm số:", font=("Arial", 14))
        self.info_label.pack(pady=10)

        # Nhãn hiển thị hình ảnh bên phải
        self.image_label = tk.Label(self.right_frame)
        self.image_label.pack()

        self.filepath = None

    def upload_image(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.filepath:
            img = Image.open(self.filepath)
            img = img.resize((550, 740))  # Điều chỉnh kích thước hình ảnh cho vừa khung
            img = ImageTk.PhotoImage(img)

            self.image_label.config(image=img)
            self.image_label.image = img

            # Kích hoạt nút chấm điểm sau khi ảnh được tải lên
            self.grade_button.config(state=tk.NORMAL)

    def grade_image(self):
        if self.filepath:
            # Tạo đối tượng Grading và thực hiện chấm điểm
            grade = Grading(self.filepath, ANSWER_KEYS, num_questions=NUM_QUESTIONS)

            student_code = grade.extract_student_code()
            test_code = grade.extract_test_code()
            score = grade.get_score()
            result_image = grade.get_result_image()

            # Cập nhật thông tin mã thí sinh, mã đề thi, điểm số
            self.info_label.config(text=f"Mã thí sinh: {student_code}\nMã đề thi: {test_code}\nĐiểm số: {score}")

            # Hiển thị ảnh kết quả chấm điểm
            cv2.imwrite("graded_image.jpg", result_image)
            graded_img = Image.open("graded_image.jpg")
            graded_img = graded_img.resize((550, 740))  # Điều chỉnh kích thước hình ảnh cho vừa khung
            graded_img = ImageTk.PhotoImage(graded_img)

            self.image_label.config(image=graded_img)
            self.image_label.image = graded_img

        else:
            messagebox.showerror("Lỗi", "Không có ảnh nào được chọn.")

# Tạo cửa sổ chính Tkinter
root = tk.Tk()
app = GradingApp(root)
root.mainloop()
