class QrData:
    def __init__(self, decoded_qr):
        polygon = decoded_qr.polygon
        self.data = decoded_qr.data
        self.center = self.__get_center(polygon)
        self.top_left = self.__get_top_left(polygon)
        self.top_right = self.__get_top_right(polygon)
        self.bottom_left = self.__get_bottom_left(polygon)
        self.bottom_right = self.__get_bottom_right(polygon)
        self.middle_top = self.__get_middle_top(polygon)
        self.middle_bottom = self.__get_middle_bottom(polygon)

    def __get_center(self, polygon):
        center_x = (polygon[0].x + polygon[1].x + polygon[2].x + polygon[3].x) // 4   
        center_y = (polygon[0].y + polygon[1].y + polygon[2].y + polygon[3].y) // 4   
        return [center_x, center_y]

    def __get_middle_top(self, polygon):
        top_left = self.__get_top_left(polygon)
        top_right = self.__get_top_right(polygon)
        middle_x = (top_left[0] + top_right[0]) // 2
        middle_y = (top_left[1] + top_right[1]) // 2
        return [middle_x, middle_y]

    def __get_middle_bottom(self, polygon):
        bottom_left = self.__get_bottom_left(polygon)
        bottom_right = self.__get_bottom_right(polygon)
        middle_x = (bottom_left[0] + bottom_right[0]) // 2
        middle_y = (bottom_left[1] + bottom_right[1]) // 2
        return [middle_x, middle_y]

    def __get_top_left(self, polygon):
        return min(self.__get_tops(polygon))

    def __get_top_right(self, polygon):
        return max(self.__get_tops(polygon))

    def __get_bottom_left(self, polygon):
        return min(self.__get_bottoms(polygon))

    def __get_bottom_right(self, polygon):
        return max(self.__get_bottoms(polygon))

    def __get_tops(self, polygon):
        return sorted(polygon, key=lambda p: p[1])[:2]

    def __get_bottoms(self, polygon):
        return sorted(polygon, key=lambda p: p[1])[2:]

    def __str__(self):
        return 'QR data: {}'.format(self.data)
