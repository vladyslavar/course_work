import sys

class Paydesk():
    def __init__(self, name):
        self.name = name
        self.queue = []
        self.tnext = sys.float_info.max


class Checkout():
    def __init__(self, name, distribution):
        self.paydesks = [
            Paydesk("Paydesk 1"),
            Paydesk("Paydesk 2"),
        ]
        self.tnext = sys.float_info.max

    def out(self):
        current_paydesk = [x for x in self.paydesks if x.tnext == self.tnext][0]
        print(f'Current paydesk: {current_paydesk.name}')

if __name__ == "__main__":
    checkout = Checkout("Checkout", None)
    checkout.paydesks[0].tnext = 10
    checkout.paydesks[1].tnext = 5
    checkout.tnext = 15
    checkout.out()

