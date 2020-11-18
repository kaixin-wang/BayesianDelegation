# Bayesian Delegation
# TestMergeAgentItem class
# Fall 2020 - Kaixin Wang

import sys
sys.path.append('../src/')

import unittest
from ddt import ddt, data, unpack
import numpy as np
import copy
import MergeAgentItem as targetCode #change to file name

@ddt
class TestMergeAgentItem(unittest.TestCase):

    # types of objects
    agents = [(2,5), (4,5)]
    plates = [(5,0), (6,1)]
    knives = [(0,4), (0,5)]
    goal = [(0,3)]
    ingredients = [(6,5), (5,6)]

    # types of status
    food_unchopped = ["Lettuce.unchopped", "Tomato.unchopped"]
    food_chopped = ["Lettuce.chopped", "Tomato.chopped"]
    food_plated = ["Lettuce.chopped.plated", "Tomato.chopped.plated"] 
    food_unchopped_plated = ["Lettuce.unchopped.plated", "Tomato.unchopped.plated"] 
    food_delivery = ["Lettuce.chopped.plated.delivery", "Tomato.chopped.plated.delivery"]
    recipe = [["Tomato.chopped.plated"], ["Lettuce.chopped.plated"]]
    
    # create the environment
    objects = {"Counter":[(0,0), (0,1), (0,2), (0,4), (0,5), (0,6),
                          (1,6), (2,6), (3,6), (4,6), (5,6), (6,6),
                          (6,5), (6,4), (6,3), (6,2), (6,1), (6,0),
                          (5,0), (4,0), (3,0), (2,0), (1,0)],
               "Goal":[(0,3)], "Knife":[(0,4), (0,5)], "Plate":[(5,0), (6,1)],
               "Lettuce":[(6,5)], "Tomato":[(5,6)], "Agent":[(2,5), (4,5)]}
    xmax = 7
    ymax = 7
    xrange = range(0,xmax)
    yrange = range(0,ymax)
    coordinates = [(x,y) for y in range(0, 7) for x in range(0, 7)]
    S = {s:{"type":None, "status":[]} for s in coordinates}
    for key, obj in objects.items():
        for pair in obj:
            S[pair]["type"] = key
            if key in ["Tomato", "Lettuce"]:
                S[pair]["status"] = "unchopped"

    # test for picking up food
    # chopped food + food
    S1 = copy.deepcopy(S); S1[agents[0]]["status"] = food_chopped[0]
    # raw food + raw food
    S2 = copy.deepcopy(S); S2[agents[0]]["status"] = food_unchopped[0]
    # [] + food -> [food]
    S3 = copy.deepcopy(S)

    # (S, X, Y, expectedXStatus, recipe)
    @data((S1, agents[0], ingredients[0], food_chopped[0], recipe),
          (S2, agents[0], ingredients[0], food_unchopped[0], recipe),
          (S3, agents[0], ingredients[0], food_unchopped[0], recipe))
    @unpack
    
    def test_pickUpFood(self, environment, x, y, expectedXStatus, recipe):
        merge = targetCode.MergeAgentItem(recipe)
        merge(environment, x, y)
        self.assertTrue(environment[x]["status"] == expectedXStatus)
        
    # test for plating food
    # chopped food + plate -> [food.chopped.plated.delivery]
    S1 = copy.deepcopy(S); S1[knives[0]]["status"] = [food_chopped[0]]; S1[agents[0]]["status"] = "Plate"
    # raw food + plate -> [food.unchopped.plated]
    S2 = copy.deepcopy(S); S2[agents[0]]["status"] = food_unchopped[0]
    # [] + plate -> [plate]
    S3 = copy.deepcopy(S)

    # (S, X, Y, XStatus, expectedXStatus, recipe)
    @data((S1, agents[0], knives[0], food_delivery[0], recipe),
          (S2, agents[0], plates[0], food_unchopped_plated[0], recipe),
          (S3, agents[0], plates[0], "Plate", recipe))
    @unpack
    
    def test_plateFood(self, environment, x, y, expectedXStatus, recipe):
        merge = targetCode.MergeAgentItem(recipe)
        merge(environment, x, y)
        self.assertTrue(environment[x]["status"] == expectedXStatus)

    # test for chopping food
    # [food.unchopped] + knife -> [food.chopped]
    S1 = copy.deepcopy(S); S1[agents[0]]["status"] = food_unchopped[0]
    # [food.chopped.plated.delivery] + knife 
    S2 = copy.deepcopy(S); S2[agents[0]]["status"] = food_delivery[0]
    # [] + knife
    S3 = copy.deepcopy(S)
    # [food.unchopped.plated] + knife -> [food.chopped.plated.delivery]
    S4 = copy.deepcopy(S); S4[agents[0]]["status"] = food_unchopped_plated[0]

    # (S, X, Y, XStatus, expectedXStatus, recipe)
    @data((S1, agents[0], knives[0], [], [food_chopped[0]], recipe),
          (S2, agents[0], knives[0], food_delivery[0], [], recipe),
          (S3, agents[0], knives[0], [], [], recipe),
          (S4, agents[0], knives[0], food_delivery[0], [], recipe))
    @unpack
    
    def test_chopFood(self, environment, x, y, expectedXStatus, expectedYStatus, recipe):
        merge = targetCode.MergeAgentItem(recipe)
        merge(environment, x, y)
        self.assertTrue(environment[x]["status"] == expectedXStatus)
        self.assertTrue(environment[y]["status"] == expectedYStatus)

    # test for delivering food
    # [food.chopped.plated.delivery] + plate
    S1 = copy.deepcopy(S); S1[agents[0]]["status"] = food_delivery[0]
    # [food.chopped.plated.delivery] + knife 
    S2 = copy.deepcopy(S); S2[agents[0]]["status"] = food_delivery[0]
    # [food.chopped.plated.delivery] + None
    S3 = copy.deepcopy(S); S3[agents[0]]["status"] = food_delivery[0]
    # [food.chopped.plated.delivery] + goal -> delivered to goal state
    S4 = copy.deepcopy(S); S4[agents[0]]["status"] = food_delivery[0]
    # [food.chopped.plated.delivery] + goal[food.chopped.plated.delivery] -> finished all deliveries
    S5 = copy.deepcopy(S); S5[agents[0]]["status"] = food_delivery[1]; S5[goal[0]]["status"] = [food_delivery[0]]
    # [food.chopped.plated.delivery] + goal[food.chopped.plated.delivery] -> finished all deliveries
    S6 = copy.deepcopy(S); S6[agents[0]]["status"] = food_delivery[0]; S6[goal[0]]["status"] = [food_delivery[1]]

    food_delivery_1 = [food_delivery[1], food_delivery[0]]

    # (S, X, Y, XStatus, expectedXStatus, recipe)
    @data((S1, agents[0], plates[0], food_delivery[0], [], recipe),
          (S2, agents[0], knives[0], food_delivery[0], [], recipe),
          (S3, agents[0], (3,3),     food_delivery[0], [], recipe),
          (S4, agents[0], goal[0],   [],               [food_delivery[0]], recipe),
          (S5, agents[0], goal[0],   [],               food_delivery,      recipe),
          (S6, agents[0], goal[0],   [],               food_delivery_1,    recipe))
    @unpack
    
    def test_deliverFood(self, environment, x, y, expectedXStatus, expectedYStatus, recipe):
        merge = targetCode.MergeAgentItem(recipe)
        merge(environment, x, y)
        self.assertTrue(environment[x]["status"] == expectedXStatus)
        self.assertTrue(environment[y]["status"] == expectedYStatus)

    def tearDown(self):
        pass
    
if __name__ == '__main__':
    unittest.main(verbosity=2)

