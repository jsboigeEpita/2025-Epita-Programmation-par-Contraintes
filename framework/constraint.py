class Constraint:
    def __init__(self):
        self.constraints = {}

    def add_constraint(self, name, constraint_function):
        """
        Adds a constraint by name.
        :param name: The name of the constraint (e.g., "max_volatility")
        :param constraint_function: A function that takes (portfolio) and returns True/False.
        """
        self.constraints[name] = constraint_function

    def check_constraints(self, portfolio):
        """
        Evaluates all constraints on a given portfolio.
        :param portfolio: The Portfolio object to test.
        :return: True if all constraints are met, False otherwise.
        """
        for name, constraint_function in self.constraints.items():
            if not constraint_function(portfolio):
                print(f"⚠️ Constraint '{name}' failed.")
                return False
        return True
