import sys
import time
import SMO
from randomizers import Randomizer

class Model():
    def __init__(self, elements):
        self.tnext = 0.0
        self.tcurr = 0.0
        self.elements = elements
        self.curr_element = None

    def simulate(self, time_modeling):
        while self.tcurr < time_modeling:
            
            print("--------------------------------------------------")
            print(f'Current time: {self.tcurr:.2f}')
            self.tnext = sys.float_info.max
            for element in self.elements:
                if element.tnext < self.tnext: # have to be <
                    self.tnext = element.tnext
                    self.curr_element = element

            prev_time = self.tcurr
            self.tcurr =  self.tnext
            for element in self.elements:
                element.tcurr = self.tcurr

            print(f'Next event: {self.curr_element.name} at {self.tnext:.2f}')
            self.curr_element.out_act()
            for element in self.elements:
                if element.tnext == self.tcurr:
                    print(f'Event: {element.name} at {self.tcurr:.2f}')
                    element.out_act()

            for element in self.elements:
                element.do_statistics(self.tcurr - prev_time)

            for element in self.elements:
                element.print_info()

            time.sleep(0)
    
    def print_results(self):
        print("END OF MODELING")
        for element in self.elements:
            element.print_info()
        
        print("STATISTICS")
        for element in self.elements:
            element.print_statistics()

if __name__ == "__main__":
    randomizer = Randomizer()
    group_randomizer = {
        "randomizer": randomizer,
        "mean_time": 30, # 30 sec, exponential
        "student_distribution": {
            "randomizer": randomizer,
            "mean_time": 0
        }
    }
    first_dishes_randomizer = {
        "randomizer": randomizer,
        "a": 50, # uniform from 50 to 120
        "b": 120 
    }
    second_dishes_randomizer = {
        "randomizer": randomizer,
        "a": 60, # uniform from 60 to 180
        "b": 180 
    }
    drinks_randomizer = {
        "randomizer": randomizer,
        "a": 5, # uniform from 5 to 20
        "b": 20 
    }
    check_out_randomizer = {
        "randomizer": randomizer,
        "a_first_dishes": 20, "b_first_dishes": 40, # uniform from 20 to 40
        "a_second_dishes": 5, "b_second_dishes": 15, # uniform from 5 to 15
        "a_drinks": 5, "b_drinks": 10 # uniform from 5 to 10
    }

    first_dishes = SMO.First_Dishes("First Dishes", first_dishes_randomizer)
    second_dishes = SMO.Second_Dishes("Second Dishes", second_dishes_randomizer)
    drinks = SMO.Drinks("Drinks", drinks_randomizer)
    check_out = SMO.Checkout("Check Out", check_out_randomizer)

    first_dishes.next_elements = { "drinks": drinks }
    second_dishes.next_elements = { "drinks": drinks }
    drinks.next_elements = {"checkout": check_out}

    student_poss_steps = {
        "first_dishes": first_dishes,
        "second_dishes": second_dishes,
        "drinks": drinks
    }
    group = SMO.Group("Group", group_randomizer, student_poss_steps)
    group.tnext = 0.0


    elements = [
        group,
        first_dishes,
        second_dishes,
        drinks, 
        check_out
    ]

    model = Model(elements)
    model.simulate(1000)
    model.print_results()
        