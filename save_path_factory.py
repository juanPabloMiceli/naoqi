from os.path import exists

class SavePathFactory:
    def __init__(self, main_path):
        self.main_path = main_path

    def get_save_path(self):
        if not exists(self.main_path):
            return self.main_path
        
        counter = 1
        
        while exists(self.__path_with_copy_number(counter)):
            counter += 1

        return self.__path_with_copy_number(counter)


    def __path_with_copy_number(self, counter):
        dot_index = self.main_path.rfind('.')
        return self.main_path[:dot_index] + str(counter) + self.main_path[dot_index:]

