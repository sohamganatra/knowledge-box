class Source_parser:
    def __init__(self):
        self.name = ""
        self.types = []

    def __init__(self, name, supported_types):
        self.name = name
        self.types = supported_types

    def supports(self, type):
        return type in self.types

    def get_name(self):
        return self.name

    def get_types(self):
        return self.types

    @staticmethod
    def parse(source):
        # the output should return list of (text chunks, start location, end location)
        raise NotImplementedError("Subclasses should implement this!")
