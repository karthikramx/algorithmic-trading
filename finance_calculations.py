


class financial_calculator:
    def __init__(self):
        print("Print Finantial calculator initalized")

    def future_value(self, present_value, rate, time):
        return round(present_value * ((1 + rate/100) ** time), 2)

    def present_value(self, future_value, rate, time):
        return  round(future_value / ((1 + rate/100) ** time), 2)

    def least_difference(self,a,b,c):
        """Returns the smallest difference between two numbers"""
        return min(abs(a-b), abs(b-c), abs(c-a))
