# Bayesian Delegation
# MergeAgentItem class
# Fall 2020 - Kaixin Wang

class MergeAgentItem():
    # initializer
    def __init__(self, recipe):
        self.counter = 0
        self.recipe = recipe
        # lists of status
        self.food = ["Lettuce", "Tomato"]
        self.food_unchopped = ["Lettuce.unchopped", "Tomato.unchopped"]
        self.food_chopped = ["Lettuce.chopped", "Tomato.chopped"]
        self.food_plated = ["Lettuce.chopped.plated", "Tomato.chopped.plated"] 
        self.food_unchopped_plated = ["Lettuce.unchopped.plated", "Tomato.unchopped.plated"] 
        self.food_delivery = ["Lettuce.chopped.plated.delivery", "Tomato.chopped.plated.delivery"]
        
    # set of helper functions
    def noPlate(self, S, X, Y):
        return len(S[X]["status"]) == 0
    def hasPlate(self, S, X, Y):
        return S[X]["status"] == "Plate"
    def isFood(self, S, X, Y):
        return S[Y]["type"] in self.food
    def isPlate(self, S, X, Y):
        return S[Y]["type"] == "Plate"
    def isKnifeStation(self, S, X, Y):
        return S[Y]["type"] == "Knife"
    def emptyKnifeStation(self, S, X, Y):
        return S[Y]["type"] == "Knife" and len(S[Y]["status"]) == 0
    def holdingUnchoppedFood(self, S, X, Y):
        return S[X]["status"] in self.food_unchopped
    def foodChopped(self, S, X, Y):
        if len(S[Y]["status"]) > 0:
            return S[Y]["status"][0] in self.food_chopped
        else:
            return False
    def unchoppedPlatedFood(self, S, X, Y):
        return S[X]["status"] in self.food_unchopped_plated
    def holdingPlate(self, S, X, Y):
        return S[X]["status"] == "Plate"
    def foodPlated(self, S, X, Y):
        if len(S[Y]["status"]) > 0:
            return S[Y]["status"][0] in self.food_plated
        else:
            return False
    def inRecipe(self, S, X, Y):
        return S[Y]["status"] in self.recipe
    def forDelivery(self, S, X, Y):
        return self.inRecipe(S, X, Y)
    def completedDelivery(self, S, X, Y):
        return set(S[Y]["status"]) == set(self.food_delivery)
    def deliverAtGoalState(self, S, X, Y):
        return S[X]["status"] in self.food_delivery and S[Y]["type"] == "Goal"
    def resetState(self):
        return {"type":"Counter", "status":[]}

    # callable
    def __call__(self, S, X, Y):
        print("x:", S[X]["type"], "y:", S[Y]["type"])
        print("x:", S[X]["status"],"y:", S[Y]["status"])
        if self.isFood(S, X, Y):
            if self.noPlate(S, X, Y):
                print("1.1 pick up the food")
                S[X]["status"] = S[Y]["type"] + ".unchopped"
                S[Y] = self.resetState()
            elif self.hasPlate(S, X, Y):
                print("1.2 pick up the food and plate it")
                S[X]["status"] = S[Y]["type"] + ".unchopped" + ".plated"
                S[Y] = self.resetState()
        elif self.holdingUnchoppedFood(S, X, Y) and self.isKnifeStation(S, X, Y):
            if self.emptyKnifeStation(S, X, Y):
                print("2. chop the food")
                if self.foodPlated(S, X, Y):
                    S[Y]['status'].append(S[X]["status"][:-10] + ".chopped.plated")
                    if self.forDelivery(S, X, Y):
                        print("2.1 out for delivery")
                        S[X]["status"] = [food + ".delivery" for food in S[Y]["status"]][0]
                        S[Y]["status"] = []
                else:
                    S[Y]['status'].append(S[X]["status"][:-10] + ".chopped")
                    S[X]['status'] = []
        elif self.noPlate(S, X, Y) and self.isPlate(S, X, Y):
            print("3. pick up the plate")
            S[X]["status"] = "Plate"
            S[Y] = self.resetState()
        elif self.holdingUnchoppedFood(S, X, Y) and self.isPlate(S, X, Y):
            print("6. pick up the plate and plate unchopped food")
            S[X]["status"] = S[X]["status"] + ".plated"
            S[Y] = self.resetState()
        elif self.isKnifeStation(S, X, Y):
            if self.holdingPlate(S, X, Y) and self.foodChopped(S, X, Y):
                print("4. plate the food")
                S[Y]["status"] = [food + ".plated" for food in S[Y]["status"]]
                S[X]["status"] = []
                if self.forDelivery(S, X, Y):
                    print("4.1 out for delivery")
                    S[X]["status"] = [food + ".delivery" for food in S[Y]["status"]][0]
                    S[Y]["status"] = []
            elif self.unchoppedPlatedFood(S, X, Y):
                print("7. chop plated raw food")
                S[Y]["status"] = [S[X]["status"].replace("unchopped", "chopped")]
                S[X]["status"] = []
                if self.forDelivery(S, X, Y):
                    print("7.1 out for delivery")
                    S[X]["status"] = [food + ".delivery" for food in S[Y]["status"]][0]
                    S[Y]["status"] = []
        elif self.deliverAtGoalState(S, X, Y):
            print("5. delivered the food")
            self.counter += 1
            S[Y]["status"].append(S[X]["status"])
            S[X]["status"] = []
            print("delivered =", self.counter)
            if self.completedDelivery(S, X, Y):
                print("finished all deliveries")
        print("x:", S[X]["type"], "y:", S[Y]["type"])
        print("x:", S[X]["status"],"y:", S[Y]["status"])

