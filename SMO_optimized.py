from randomizers import Randomizer
import sys
import time
import random
import copy


class Element:
    id = 0
    def __init__(self, name, distribution):
        self.id = Element.id
        Element.id += 1
        self.name = name if name != None else "Element " + str(self.id)
        self.tnext = 0.001
        self.tcurr = 0.0
        self.dist = distribution
        self.state = 0
        self.next_elements = None

        self.mean_queue_sum = 0.0
        self.max_queue = 0

    def in_act(self):
        pass

    def out_act(self):
        pass

    def print_info(self):
        print(f'Element: {self.name}, State: {self.state}, tcurr: {self.tcurr:.2f}, tnext: {(self.tnext if self.tnext != sys.float_info.max else 0):.2f}')
        # print()
        
    def do_statistics(self, deltaT):
        pass

    def print_statistics(self):
        print(f'Element: {self.name}, Mean queue: {self.mean_queue_sum / self.tcurr:.2f}, Max queue: {self.max_queue}')


class Group(Element):
    def __init__(self, name, distribution, student_poss_steps):
        super().__init__(name, distribution)
        self.group_id = 0
        self.students = []
        self.student_poss_steps = student_poss_steps
        self.students_quantity = 0

    def out_act(self):
        self.tnext = self.tcurr + self.dist["randomizer"].Exp(self.dist["mean_time"])
        rand_size = random.randint(1, 100)
        if rand_size <= 50:
            student_group_size = 1
        elif rand_size <= 80:
            student_group_size = 2
        elif rand_size <= 90:
            student_group_size = 3
        else:
            student_group_size = 4 
        print(f'\nGroup {self.group_id} came to the canteen. Size: {student_group_size}')
        self.students_quantity += student_group_size

        for i in range(student_group_size):
            self.students.append(Student(f'Student {len(self.students)} from Group {self.group_id}', self.dist['student_distribution'], self.student_poss_steps))
        for student in self.students:
            student.out_act()
        print()

        self.group_id += 1
        self.students = []

    def print_info(self):
        super().print_info()
        print(f'Students has come to canteen: {self.students_quantity}')
        print()
        

class Student(Element):
    def __init__(self, name, distribution, student_poss_steps):
        super().__init__(name, distribution)
        self.in_first_dishes = False
        self.in_second_dishes = False
        self.in_drinks = False
        self.in_checkout = False
        self.possible_next_elements = student_poss_steps

    def out_act(self):
        self.tnext = self.tcurr
        
        rand_way = random.randint(0, 100)
        if rand_way <= 80:
            self.next_elements = [self.possible_next_elements["first_dishes"]] # first dishes
        elif rand_way <= 95:
            self.next_elements = [self.possible_next_elements["second_dishes"]] # second dishes
        else:
            self.next_elements = [self.possible_next_elements["drinks"]] # drinks

        if self.next_elements != None:
            for element in self.next_elements:
                student_to_send = copy.copy(self)
                element.in_act(student_to_send)
    
class First_Dishes_Worker():
    def __init__(self, name) -> None:
        self.name = name
        self.tnext = sys.float_info.max
        self.queue = []
        self.state = 0
        self.student_processing = None

        self.received_students = 0
        self.proccessed_students = 0
        self.mean_queue_sum = 0.0
        self.max_queue = 0
        self.mean_waiting_time = 0.0
        self.max_waiting_time = 0.0

class First_Dishes(Element):
    def __init__(self, name, distribution):
        super().__init__(name, distribution)
        self.tnext = sys.float_info.max
        self.first_dishes_workers = [
            First_Dishes_Worker("First Dishes Worker 1"),
            First_Dishes_Worker("First Dishes Worker 2"),
            First_Dishes_Worker("First Dishes Worker 3"),
            First_Dishes_Worker("First Dishes Worker 4"),
            First_Dishes_Worker("First Dishes Worker 5"),
        ] 

    def in_act(self, student):
        print(f'{student.name} came to {self.name}')

        #chekc if it is free worker
        worker_to_use = None
        for worker in self.first_dishes_workers:
            if worker.state == 0:
                worker_to_use = worker
                break
        # go to free worker
        if worker_to_use is not None:
            worker_to_use.state = 1
            worker_to_use.student_processing = student
            worker_to_use.received_students += 1

            time_of_service = self.dist["randomizer"].Uniform(self.dist["a"], self.dist["b"])
            worker_to_use.tnext = self.tcurr + time_of_service
            print(f'{student.name} will get his first dishes for {time_of_service:.2f}')
            self.tnext = min(self.first_dishes_workers, key=lambda x: x.tnext).tnext    
        # place in min queue
        else:
            worker_with_min_queue = min(self.first_dishes_workers, key=lambda x: x.queue.__len__())
            worker_with_min_queue.queue.append(student)
            worker_with_min_queue.received_students += 1
            print(f'{student.name} will wait in queue for {worker_with_min_queue.queue.__len__()} students')

    def out_act(self):
        super().out_act()
        current_worker = [x for x in self.first_dishes_workers if x.tnext == self.tnext][0]
        current_student = copy.copy(current_worker.student_processing)
        current_worker.state = 0
        current_worker.student_processing = None
        current_worker.tnext = sys.float_info.max
        current_worker.proccessed_students += 1

        if current_worker.queue.__len__() > 0:
            current_worker.state = 1
            current_worker.student_processing = current_worker.queue.pop(0)
            time_of_service = self.dist["randomizer"].Uniform(self.dist["a"], self.dist["b"])
            current_worker.tnext = self.tcurr + time_of_service
            print(f'{current_worker.student_processing.name} will get his first dishes for {time_of_service:.2f}')

        self.tnext = min(self.first_dishes_workers, key=lambda x: x.tnext).tnext

        self.next_elements["drinks"].in_act(current_student)


    def print_info(self):
        super().print_info()
        for worker in self.first_dishes_workers:
            print(f'Worker: {worker.name}, Queue: {worker.queue.__len__()}, State: {worker.state}, tnext: {(worker.tnext if worker.tnext != sys.float_info.max else 0):.2f}')
            print(f'Received students: {worker.received_students}; Proccessed students: {worker.proccessed_students}')
        print()

    def do_statistics(self, deltaT):
        for worker in self.first_dishes_workers:
            worker.mean_queue_sum += worker.queue.__len__() * deltaT
            if worker.queue.__len__() > worker.max_queue:
                worker.max_queue = worker.queue.__len__()

    def print_statistics(self):
        for worker in self.first_dishes_workers:
            print(f'Worker: {worker.name}, Mean queue: {worker.mean_queue_sum / self.tcurr:.2f}, Max queue: {worker.max_queue}')
            worker.mean_waiting_time = worker.mean_queue_sum / worker.proccessed_students if worker.proccessed_students != 0 else 0
            worker.max_waiting_time = (worker.mean_waiting_time / (worker.mean_queue_sum / self.tcurr)) * worker.max_queue if worker.mean_queue_sum != 0 else 0
            print(f'Mean waiting time: {worker.mean_waiting_time:.2f}, Max waiting time: {worker.max_waiting_time:.2f}')
        print()
        


class Second_Dishes(Element):
    def __init__(self, name, distribution):
        super().__init__(name, distribution)
        self.tnext = sys.float_info.max
        self.queue = []
        self.state = 0
        self.student_processing = None

        self.received_students = 0
        self.proccessed_students = 0
        self.mean_waiting_time = 0.0
        self.max_waiting_time = 0.0

    def in_act(self, student):
        print(f'{student.name} came to {self.name}')
        self.received_students += 1
        if self.state == 0:
            self.state = 1
            self.tnext = self.tcurr + self.dist["randomizer"].Uniform(self.dist["a"], self.dist["b"])
            self.student_processing = student
            self.student_processing.in_second_dishes = True

        else:
            self.queue.append(student)

    def out_act(self):
        super().out_act()
        student_to_send = copy.copy(self.student_processing)

        self.tnext = sys.float_info.max
        self.student_processing = None
        self.state = 0

        self.next_elements["drinks"].in_act(student_to_send)
        self.proccessed_students += 1

        if len(self.queue) > 0:
            self.state = 1
            self.tnext = self.tcurr + self.dist["randomizer"].Uniform(self.dist["a"], self.dist["b"])
            self.student_processing = self.queue.pop(0)
            self.student_processing.in_second_dishes = True

    def print_info(self):
        super().print_info()
        print(f'Queue: {self.queue.__len__()}')
        print(f'Received students: {self.received_students}; Proccessed students: {self.proccessed_students}')
        print()

    def do_statistics(self, deltaT):
        self.mean_queue_sum += self.queue.__len__() * deltaT
        if self.queue.__len__() > self.max_queue:
            self.max_queue = self.queue.__len__()

    def print_statistics(self):
        super().print_statistics()
        self.mean_waiting_time = self.mean_queue_sum / self.proccessed_students if self.proccessed_students != 0 else 0
        self.max_waiting_time = (self.mean_waiting_time / (self.mean_queue_sum / self.tcurr)) * self.max_queue if self.mean_queue_sum != 0 else 0
        print(f'Mean waiting time: {self.mean_waiting_time:.2f}, Max waiting time: {self.max_waiting_time:.2f}')
        print()


class Drinks(Element):
    def __init__(self, name, distribution):
        super().__init__(name, distribution)
        self.queue = []
        self.tnext = sys.float_info.max

        self.received_students = 0
        self.proccessed_students = 0
        self.mean_waiting_time = 0.0
        self.max_waiting_time = 0.0

    def in_act(self, student):
        print(f'{student.name} came to {self.name}')
        self.received_students += 1
        student.in_drinks = True

        tdrink = self.tcurr + self.dist["randomizer"].Uniform(self.dist["a"], self.dist["b"])
        self.queue.append([student, tdrink])
        print(f'{student.name} will get his drink for {(tdrink - self.tcurr):.2f}')

        # min tdrink in queue
        next_time = min(self.queue, key=lambda x: x[1])[1]
        self.tnext = next_time
        print(f'Current queue: {self.queue.__len__()}')
        for student in self.queue:
            print(f'{student[0].name}, time(tdrink): {student[1]:.2f}')
        print(f'Next drink will be taken in {next_time:.2f}')

    def out_act(self):
        super().out_act()
        current_student = [x for x in self.queue if x[1] == self.tnext][0][0]
        self.queue.remove([current_student, self.tnext])
        self.tnext = sys.float_info.max
        self.proccessed_students += 1

        if self.queue.__len__() > 0:
            next_time = min(self.queue, key=lambda x: x[1])[1]
            self.tnext = next_time
            print(f'Current queue: {self.queue.__len__()}')
            for student in self.queue:
                print(f'{student[0].name}, time(tdrink): {student[1]:.2f}')
            print(f'Next drink will be taken in {next_time:.2f}')

        if self.next_elements is not None:
            student_to_send = copy.copy(current_student)
            self.next_elements["checkout"].in_act(student_to_send)

    def print_info(self):
        super().print_info()
        print(f'Processing: {self.queue.__len__()}')
        print(f'Received students: {self.received_students}; Proccessed students: {self.proccessed_students}')
        print()

    def do_statistics(self, deltaT):
        self.mean_queue_sum += self.queue.__len__() * deltaT
        if self.queue.__len__() > self.max_queue:
            self.max_queue = self.queue.__len__()

    def print_statistics(self):
        super().print_statistics()
        self.mean_waiting_time = self.mean_queue_sum / self.proccessed_students if self.proccessed_students != 0 else 0
        self.max_waiting_time = (self.mean_waiting_time / (self.mean_queue_sum / self.tcurr)) * self.max_queue if self.mean_queue_sum != 0 else 0
        print(f'Mean waiting time: {self.mean_waiting_time:.2f}, Max waiting time: {self.max_waiting_time:.2f}')
        print()


class Paydesk():
    def __init__(self, name):
        self.name = name
        self.queue = []
        self.state = 0
        self.student_processing = None
        self.tnext = sys.float_info.max

        self.received_students = 0
        self.proccessed_students = 0
        self.mean_queue_sum = 0.0
        self.max_queue = 0
        self.mean_waiting_time = 0.0
        self.max_waiting_time = 0.0

class Checkout(Element):
    def __init__(self, name, distribution):
        super().__init__(name, distribution)
        self.paydesks = [
            Paydesk("Paydesk 1"),
            Paydesk("Paydesk 2"),
        ]
        self.tnext = sys.float_info.max
        

    def in_act(self, student):
        print(f'{student.name} came to {self.name}')

        #chekc if it is free paydesk
        paydesk_to_use = None
        for paydesk in self.paydesks:
            if paydesk.state == 0:
                paydesk_to_use = paydesk
                break
        # go to free  paydesk
        if paydesk_to_use is not None:
            paydesk_to_use.state = 1
            paydesk_to_use.student_processing = student
            paydesk_to_use.received_students += 1

            time_of_service = 0
            if student.in_first_dishes:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_first_dishes"], self.dist["b_first_dishes"])
            if student.in_second_dishes:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_second_dishes"], self.dist["b_second_dishes"])
            if student.in_drinks:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_drinks"], self.dist["b_drinks"])
            paydesk_to_use.tnext = self.tcurr + time_of_service
            print(f'{student.name} will pay for his food for {time_of_service:.2f}')
            self.tnext = min(self.paydesks, key=lambda x: x.tnext).tnext
        # place in min queue
        else:
            paydesk_with_min_queue = min(self.paydesks, key=lambda x: x.queue.__len__())
            paydesk_with_min_queue.queue.append(student)
            paydesk_with_min_queue.received_students += 1
            print(f'{student.name} will wait in queue for {paydesk_with_min_queue.queue.__len__()} students')

    def out_act(self):
        super().out_act()
        print(f'{self.name} out_act')
        print(f'Current time: {self.tcurr:.2f}')
        print(f'Next time: {self.tnext:.2f}')

        current_paydesk = [x for x in self.paydesks if x.tnext == self.tnext][0]
        current_student = current_paydesk.student_processing
        current_paydesk.state = 0
        current_paydesk.student_processing = None
        current_paydesk.tnext = sys.float_info.max
        current_paydesk.proccessed_students += 1

        if current_paydesk.queue.__len__() > 0:
            current_paydesk.state = 1
            current_paydesk.student_processing = current_paydesk.queue.pop(0)
            time_of_service = 0
            if current_paydesk.student_processing.in_first_dishes:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_first_dishes"], self.dist["b_first_dishes"])
            if current_paydesk.student_processing.in_second_dishes:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_second_dishes"], self.dist["b_second_dishes"])
            if current_paydesk.student_processing.in_drinks:
                time_of_service += self.dist["randomizer"].Uniform(self.dist["a_drinks"], self.dist["b_drinks"])
            current_paydesk.tnext = self.tcurr + time_of_service
            print(f'{current_paydesk.student_processing.name} will pay for his food for {time_of_service:.2f}')

            
        self.tnext = min(self.paydesks, key=lambda x: x.tnext).tnext

    
    def print_info(self):
        super().print_info()
        for paydesk in self.paydesks:
            print(f'Paydesk: {paydesk.name}, Queue: {paydesk.queue.__len__()}, State: {paydesk.state}, tnext: {(paydesk.tnext if paydesk.tnext != sys.float_info.max else 0):.2f}')
            print(f'Received students: {paydesk.received_students}; Proccessed students: {paydesk.proccessed_students}')
        print()

    def do_statistics(self, deltaT):
        for paydesk in self.paydesks:
            paydesk.mean_queue_sum += paydesk.queue.__len__() * deltaT
            if paydesk.queue.__len__() > paydesk.max_queue:
                paydesk.max_queue = paydesk.queue.__len__()

    def print_statistics(self):
        for paydesk in self.paydesks:
            print(f'Paydesk: {paydesk.name}, Mean queue: {paydesk.mean_queue_sum / self.tcurr:.2f}, Max queue: {paydesk.max_queue}')
            paydesk.mean_waiting_time = paydesk.mean_queue_sum / paydesk.proccessed_students if paydesk.proccessed_students != 0 else 0
            paydesk.max_waiting_time = (paydesk.mean_waiting_time / (paydesk.mean_queue_sum / self.tcurr)) * paydesk.max_queue if paydesk.mean_queue_sum != 0 else 0
            print(f'Mean waiting time: {paydesk.mean_waiting_time:.2f}, Max waiting time: {paydesk.max_waiting_time:.2f}')
        print()
                
