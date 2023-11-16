import sys
import time
import SMO_optimized as SMO
from randomizers import Randomizer

class Model():
    def __init__(self, elements):
        self.tnext = 0.0
        self.tcurr = 0.0
        self.elements = elements
        self.curr_element = None

        self.max_clients = 0
        self.mean_clients_sum = 0

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
            self.make_canteen_statistics(self.tcurr - prev_time)

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

        print(f'Mean clients in canteen: {self.mean_clients_sum / self.tcurr:.2f}, max clients: {self.max_clients}')
        
        print(f'Route first_dishes -> drinks -> checkout:')
        first_route_mean_time = 0.0
        first_route_max_time = 0.0
        for element in self.elements:
            if isinstance(element, SMO.First_Dishes):
                for worker in element.first_dishes_workers:
                    first_route_mean_time += worker.mean_waiting_time / element.first_dishes_workers.__len__()
                    first_route_max_time += worker.max_waiting_time / element.first_dishes_workers.__len__()
            elif isinstance(element, SMO.Drinks):
                first_route_mean_time += element.mean_waiting_time
                first_route_max_time += element.max_waiting_time
            elif isinstance(element, SMO.Checkout):
                for paydesk in element.paydesks:
                    first_route_mean_time += paydesk.mean_waiting_time / element.paydesks.__len__()
                    first_route_max_time += paydesk.max_waiting_time / element.paydesks.__len__()
        print(f'Mean waiting time: {first_route_mean_time:.2f}, max waiting time: {first_route_max_time:.2f}')

        print(f'Route second_dishes -> drinks -> checkout:')
        second_route_mean_time = 0.0
        second_route_max_time = 0.0
        for element in self.elements:
            if isinstance(element, SMO.Second_Dishes) or isinstance(element, SMO.Drinks):
                second_route_mean_time += element.mean_waiting_time
                second_route_max_time += element.max_waiting_time
            if isinstance(element, SMO.Checkout):
                for paydesk in element.paydesks:
                    second_route_mean_time += paydesk.mean_waiting_time / element.paydesks.__len__()
                    second_route_max_time += paydesk.max_waiting_time / element.paydesks.__len__()
        print(f'Mean waiting time: {second_route_mean_time:.2f}, max waiting time: {second_route_max_time:.2f}')

        print(f'Route drinks -> checkout:')
        third_route_mean_time = 0.0
        third_route_max_time = 0.0
        for element in self.elements:
            if isinstance(element, SMO.Drinks):
                third_route_mean_time += element.mean_waiting_time
                third_route_max_time += element.max_waiting_time
            if isinstance(element, SMO.Checkout):
                for paydesk in element.paydesks:
                    third_route_mean_time += paydesk.mean_waiting_time / element.paydesks.__len__()
                    third_route_max_time += paydesk.max_waiting_time / element.paydesks.__len__()
        print(f'Mean waiting time: {third_route_mean_time:.2f}, max waiting time: {third_route_max_time:.2f}')
            
        

    # TODO: make statistics for canteen
    # for first_dishes, second_dishes queue + person proccessitng
    # for drinks queue
    # for checkout queue + person processing is each paydesk
    def make_canteen_statistics(self, deltaT):
        all_clients = 0
        for element in self.elements:
            if isinstance(element, SMO.First_Dishes):
                for worker in element.first_dishes_workers:
                    all_clients += worker.queue.__len__()
                    if worker.state == 1:
                        all_clients += 1
            elif isinstance(element, SMO.Second_Dishes):
                all_clients += element.queue.__len__()
                if element.state == 1:
                    all_clients += 1
            elif isinstance(element, SMO.Drinks):
                all_clients += element.queue.__len__()
            elif isinstance(element, SMO.Checkout):
                for paydesk in element.paydesks:
                    all_clients += paydesk.queue.__len__()
                    if paydesk.state == 1:
                        all_clients += 1

        self.mean_clients_sum += all_clients * deltaT
        if all_clients > self.max_clients:
            self.max_clients = all_clients
                
            

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
    model.simulate(5400)
    model.print_results()
        