import argparse


class Analyer():
    def __init__(self, path):
        self.excel = None

    def get_data_name(self):
        pass

    def get_function(self):
        pass
    
    def get_case(self):
        pass


class Elem():
    def __init__(self, str):
        pass


class Module():
    def __init__(self):
        pass


class Function():
    def __init__(self):
        pass


class ContextEnv():
    def __init__(self):
        self.env = []
    
    def push(self):
         pass
    
    def pop(self):
        pass


class Generator():
    def __init__(self, path):
        self.analyer = Analyer(path)
        self.env = ContextEnv()

    def generate(self):
        self.__gen_glo

    def __gen_data(self):
        pass
    
    def __gen_case(self):
        pass

    def __gen_global(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i')
    parser.add_argument('-o')

    args = parser.parse_args()
    
    input = args.i
    ouput = args.o

    gen = Generator(input)
