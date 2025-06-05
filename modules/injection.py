
class Injection:
    def __init__(self, text, priority, name: str="user"):
        self.text = text
        self.priority = priority
        self.name = name

    def __str__(self):
        return self.text
