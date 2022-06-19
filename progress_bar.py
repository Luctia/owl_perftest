class ProgressBar():
    def __init__(self, total, progress=0):
        self.total = total
        self.progress = progress

    def done_with_step(self):
        self.progress += 1
        self.print_bar()

    def finish(self):
        self.progress = self.total
        self.print_bar()

    def print_bar(self):
        percent = 100 * (self.progress / float(self.total))
        bar = '█' * int(percent) + '-' * int(100 - percent)
        print(f"\r|{bar}| {percent:.2f}%", end="\r")
