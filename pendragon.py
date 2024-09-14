import cv2
import numpy as np
from detect import Detect

class Grading:
    def __init__(self, path, answer_keys, num_questions=40):
        self.num_questions = num_questions
        self.answer_keys = answer_keys[:self.num_questions]
    
        self.detector = Detect(path, find_exam=False)
        self.origin_image = self.detector.get_exam()
        self.result_image = self.origin_image.copy()
        self.answers = self.get_answers()
    def get_answers(self):
        full_answers = []
        for index_sheet, (points, sheet) in enumerate(self.detector.get_sheet_ans()):
            if len(full_answers) >= self.num_questions:
                break
            start_width = int(sheet.shape[1] * 0.18)
            sheet = sheet[:, start_width:]

            part_height = sheet.shape[0] // 6
            parts = [sheet[i*part_height:(i+1)*part_height, :] for i in range(6)]

            for index, five_ans in enumerate(parts):
                start_key, end_key = index_sheet*30 + index*5, min(index_sheet*30 + (index+1)*5, self.num_questions)
                # print(start_key, end_key)
                keys = self.answer_keys[start_key: end_key]

                start_points = points[0] + start_width, points[1] + index*part_height
                num_ans = len(full_answers)
                full_answers += self.grading_sheet(start_points, five_ans, keys, num_ans)

        return np.array(full_answers)
    def grading_sheet(self,points, img, keys, num_ans):
        n_row, n_col = 5,4
        (start_x, start_y)  = points

        padding_y = 16
        start_y += padding_y
        img = img[padding_y:-padding_y,0:-5]

        height, width, _ = img.shape
        row_height = height / n_row
        col_width = width / n_col

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, height / (n_row*2),
                                param1=200, param2=10,
                                minRadius=8, maxRadius=16)
        circles = np.uint16(np.around(circles))

        dic_idx2char = {0:'A',1:'B',2:'C',3:'D'}
        _, thresh = cv2.threshold(gray, 200, 255, 0)
        answers = ['-'] * n_row
        color = {"correct":(0, 255, 0),
                "incorrect":(0,0,255),
                "key":(255,0,0)}
        # Dữ liệu của từng hàng, mỗi hàng gồm 4 circle
        data = {str(i): [] for i in range(n_row)}
        for i in circles[0, :]:
            x, y, radius = i
            row_idx = int(y / row_height )
            data[str(row_idx)].append(i)
        cnt_ans = num_ans
        for row in data:
            cnt_ans += 1
            if cnt_ans > self.num_questions:
                return answers
            
            for circle in data[row]:
                x, y, radius = circle
                row_idx = int(row)
                col_idx = int(x / col_width )

                # Vẽ circle của key
                if dic_idx2char[col_idx] == keys[row_idx]:
                    x_key, y_key = start_x + x, start_y + y
                    cv2.circle(self.result_image, (x_key, y_key), radius, color['key'], 3)

                mask = np.zeros_like(thresh)
                cv2.circle(mask, (x, y), radius, 255, -1)
                mean_val = cv2.mean(thresh, mask=mask)[0]

                if mean_val < 50:
                    if answers[row_idx] == '-':
                        answers[row_idx] = dic_idx2char[col_idx] 
                        x_ans, y_ans = start_x + x, start_y + y
                        cv2.circle(self.result_image, ( x_ans, y_ans), radius, color['correct'] if answers[row_idx] == keys[row_idx] else color['incorrect'], 3)
                    else: # Chọn 2 đáp án cho cút
                        answers[row_idx] = 'X'
        return answers
    def get_score(self):
        correct = self.answers[:self.num_questions] == self.answer_keys[:self.num_questions]
        score = (sum(correct) / self.num_questions) * 10
        return score
    def extract_code(self, points, img, name='student_code'):
        n_row, n_col = 10, 6
        if name != 'student_code':
            n_col = 3
        start_x, start_y, width, height = points

        row_height = height / n_row
        col_width = width / n_col

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, height / (n_row*2),
                                   param1=200, param2=30,
                                   minRadius=10, maxRadius=16)
        code = [''] * n_col
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                x, y, radius = i
                row_idx = int(y // row_height)
                col_idx = int(x // col_width)
                code[col_idx] = str(row_idx)

                x_true, y_true = start_x + x, start_y + y
                cv2.circle(self.result_image, (x_true, y_true), radius, (0, 255, 0), 4)
                cv2.putText(self.result_image, str(row_idx), (start_x + x - 10, start_y - 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        return ''.join(code)

    def extract_student_code(self):
        points, img = self.detector.get_student_code()[0]
        return self.extract_code(points, img, "student_code")

    def extract_test_code(self):
        points, img = self.detector.get_test_code()[0]
        return self.extract_code(points, img, "test_code")
    def get_result_image(self):
        return self.result_image
    

