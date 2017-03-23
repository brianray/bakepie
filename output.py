# coding: utf-8
import fractions
import copy

solids = ("flour", "sugar", "salt", "shortening")
liquids = ("water", "spice")
large_items = ("apples", "eggs")


class IngredientBase:
    " Base class for common functionality "
    
    target = ()
        
    def __init__(self, ingredient_str):
        self.original_ingredient_str = ingredient_str
        self.parse_parts(ingredient_str)
        self.normalize_qty()
        
    def __repr__(self):
        return "<Ingredient ({}): {} - {} {}>".format(self.name,
                                                     self.item,
                                                     self.qty,
                                                     self.unit)
        
    def parse_parts(self, ingredient_str):
        parts = ingredient_str.split()
        self.qty = parts[0]
        self.qty_max = 0
        self.unit = parts[1]
        self.item = " ".join(parts[2:])
        if self.unit == "to" or "-" in self.qty: # means a range was enetered
            if "-" in self.qty:
                minsize, maxsize = self.qty.split("-")
                self.qty = minsize
                self.qty_max = maxsize
            else:  # to
                self.qty = parts[0]
                self.qty_max = parts[2]
                self.unit = parts[3]
                self.item = " ".join(parts[4:])
    
    def does_match_target(self, subject_str):
        """ Checks if any of the strings in self.target exitst in subject_str
            returns: True or False
        """
        for item in self.target:
            if item.lower() in subject_str.lower():
                return True
        return False

    def normalize_qty(self):
        self.qty = fractions.Fraction(self.qty)
    
    def copy(self):
        return copy.copy(self)
    
    def empty(self):
        to_empty = self.copy()
        to_empty.qty = fractions.Fraction(0)
        return to_empty

class DrySolid(IngredientBase):
    "class for dry solids, like sugar or flour"
    name = "solid"
    target = solids
    
class Liquid(IngredientBase):
    "class for liquids, like milk or beer"
    name = "liquid"
    target = liquids
    
class LargeItem(IngredientBase):
    "class for items, like an egg or apple"
    name = "large item"
    target = large_items

    def parse_parts(self, ingredient_str):
        parts = ingredient_str.split()
        self.qty = parts[0]
        self.qty_max = 0
        self.unit = "item"
        self.item = " ".join(parts[1:])
        if self.unit == "to" or "-" in self.qty: # means a range was enetered
            if "-" in self.qty:
                minsize, maxsize = self.qty.split("-")
                self.qty = minsize
                self.qty_max = maxsize
            else:  # to
                self.qty = parts[0]
                self.qty_max = parts[2]
                self.unit = "item"
                self.item = " ".join(parts[3:])                

    
def return_instance(ingredient):
    "given an ingredient string, return the intance"
    instance = None
    if is_ingredient_in_list(solids, ingredient):
        instance = DrySolid(ingredient) #<-- now put it here
    elif is_ingredient_in_list(liquids, ingredient):
        instance = Liquid(ingredient) #<-- and here
    elif is_ingredient_in_list(large_items, ingredient):
        instance = LargeItem(ingredient) #<-- and here
    else:
        raise Exception("don't know what is '{}'".format(ingredient))
    # removed the parse call
    return instance 

def is_ingredient_in_list(the_list, ingredient_string):
    "if any item "
    for list_item in the_list:
        if list_item in ingredient_string:
            return True
    return False
