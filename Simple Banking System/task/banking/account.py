import random
from sqlite_operations import DatabaseManager, TABLE_COLUMNS, TABLE_CARDS, SQL_NAME


class Account:
    db = DatabaseManager(SQL_NAME)
    db.create_table(TABLE_CARDS, TABLE_COLUMNS)

    def __init__(self, iin: str, balance: int):
        self.id = 1
        self.iin = iin
        self.card_number = None
        self.pin = None
        self.store = dict()
        self.balance = balance

    def select_create_log_exit(self):
        choices = {'1': self.create_account,
                   '2': self.log_into_account,
                   '0': self.exit}
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')
        while True:
            choice = input()
            if not choices[choice]():
                return False

    def exit(self):
        print("Bye")
        return False

    def check_number_with_luhn_algorithm(self, card_number_to_check: str) -> int:
        card_number_to_check = [int(x) for x in card_number_to_check]
        for m in range(0, len(card_number_to_check), 2):
            if card_number_to_check[m] * 2 < 9:
                card_number_to_check[m] = card_number_to_check[m] * 2
            elif card_number_to_check[m] * 2 >= 9:
                card_number_to_check[m] = (card_number_to_check[m] * 2) - 9
        return sum(card_number_to_check)

    def generate_check_sum(self, luhn_alg_result: int) -> str:
        check_sum_ = 0
        while (luhn_alg_result + check_sum_) % 10 != 0:
            check_sum_ += 1
        return str(check_sum_)

    def generate_card_number(self) -> str:
        customer_account_number = ''.join(map(str, [random.randint(0, 9) for _ in range(9)]))
        iin_caa = self.iin + customer_account_number  # issuer_ident_num  + customer_account_num
        luhn_alg_res = self.check_number_with_luhn_algorithm(iin_caa)  # Luhn algorithm
        check_sum = self.generate_check_sum(luhn_alg_res)  # search for checksum
        card_number = self.iin + customer_account_number + check_sum
        return card_number

    def generate_pin(self):
        return ''.join(map(str, [random.randint(0, 9) for _ in range(4)]))

    def create_account(self):
        random.seed()
        self.card_number = self.generate_card_number()
        self.pin = self.generate_pin()
        print('Your card has been created')
        print('Your card number:')
        print(int(self.card_number))
        print('Your card PIN:')
        print(int(self.pin))
        self.db.add('card',
                    '(id, number, pin, balance)',
                    f'({self.id}, {self.card_number}, {self.pin}, {self.balance})')
        self.id += 1
        return True

    def add_income(self):
        self.balance += int(input('Enter income:\n'))
        self.db.update_table('card',
                             self.balance,
                             'number',
                             self.card_number)
        select_card_info_from_db = self.db.fetch_one_by_card_number('card',
                                                                    self.card_number)
        self.balance = select_card_info_from_db[3]
        print('Income was added!')

    def check_transfer_conditions(self, number: str) -> bool:
        if (self.check_number_with_luhn_algorithm(number[:-1]) + int(number[-1])) % 10 != 0:
            print('Probably you made a mistake in the card number. Please try again!')
            return False
        elif not self.db.fetch_one_by_card_number('card', number):
            print('Such a card does not exist.')
            return False
        return True

    def transfer_balance(self):
        print('Transfer')
        print('Enter card number:\n')
        card_number_to_transfer = input()
        if self.check_transfer_conditions(card_number_to_transfer):
            amount_money_to_transfer = int(input('Enter how much money you want to transfer:\n'))
            if amount_money_to_transfer > self.balance:
                print('Not enough money!')
            else:
                # update current card balance (-)
                self.balance -= amount_money_to_transfer
                self.db.update_table('card',
                                     self.balance,
                                     'number',
                                     self.card_number)
                # change balance of card to transfer (+)
                card_transfer_to_info = self.db.fetch_one_by_card_number('card',
                                                                         card_number_to_transfer)
                balance_after_transfer = card_transfer_to_info[3] + amount_money_to_transfer
                self.db.update_table('card',
                                     balance_after_transfer,
                                     'number',
                                     card_number_to_transfer)
                print('Success!')

    def log_into_account(self) -> bool:
        print('Enter your card number:')
        self.card_number = input()
        print('Enter your PIN:')
        self.pin = input()

        #  select_card_info_from_db
        card_info_from_db = self.db.fetch_one_by_card_number('card', self.card_number)
        # Check db_account details with new input data
        try:
            if card_info_from_db[1] != self.card_number or card_info_from_db[2] != self.pin:
                print('Wrong card number or PIN!')
                return True
            else:
                self.id = card_info_from_db[0]
                self.balance = card_info_from_db[3]
                print('You have successfully logged in!')
                while True:
                    if not self.operate_account_menu():
                        return False
        except TypeError:  # None means there is no data card_info_from_db (i.e. card_number) in the db
            print('Wrong card number or PIN!')
            return True

    def operate_account_menu(self):
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')
        after_log_choice = input()
        if after_log_choice == '0':
            return self.exit()
        elif after_log_choice == '1':
            balance = self.db.fetch_one_by_card_number('card', self.card_number)[3]
            print('Balance:', balance)
        elif after_log_choice == '2':
            self.add_income()
        elif after_log_choice == '3':
            self.transfer_balance()
        elif after_log_choice == '4':
            self.db.delete_row('card', 'number', self.card_number)
            print('The account has been closed!')
        elif after_log_choice == '5':
            print('You have successfully logged out!')
            return self.select_create_log_exit()
        return True
