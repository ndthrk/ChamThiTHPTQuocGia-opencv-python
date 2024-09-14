import cv2
import artoria as pendragon

class Detect():
    width, height = 1830, 2560
    def __init__(self, path_image, find_exam=False):
        self.image = cv2.resize(cv2.imread(path_image), (self.width, self.height))
        if find_exam:
            self.image = self._find_exam()
    def _find_exam(self):
        contours = pendragon.get_contours(self.image, minArea=300000)
        points_exam_paper = pendragon.get_4_contour(contours[0][2])
        return pendragon.wrap_image(self.image, points_exam_paper, self.width, self.height)
    def get_exam(self):
        return self.image
    def get_sheet_ans(self):
        return pendragon.extract_part_area(self.image, "sheet_ans")
    def get_test_code(self):
        return pendragon.extract_part_area(self.image, "test_code")
    def get_student_code(self):
        return pendragon.extract_part_area(self.image, "student_code")
