import uuid
import copy
import sys
import os
import random
from collections import defaultdict

import prettytable

from output import (LargeItem,
                    IngredientBase,
                    Liquid,
                    return_instance,
                    is_ingredient_in_list)
from pie_logger import get_logger
log = get_logger()


class Recipe:

    def __init__(self, pie_instance, path):
        self.ingredients = {}
        self.steps = {}
        self.pie_class_name = type(pie_instance).__name__
        self.path = path

        # read_recipe
        self.read_recipe()
        # get title
        self.get_title()
        # get crust and filling
        self.get_crust_filling()

        self.get_ingredients_as_list("filling")
        self.get_the_steps_as_list("filling")
        self.get_ingredients_as_list("crust")
        self.get_the_steps_as_list("crust")

    def get_ingredients_as_list(self, which):
        recipe_part = getattr(self, which)
        ingredients = recipe_part.split("\n\n")[0]
        self.ingredients[which] = ingredients.split("\n")

    def get_the_steps_as_list(self, which):
        recipe_part = getattr(self, which)
        self.steps[which] = recipe_part.split("\n\n")[1:]

    def read_recipe(self):
        self.recipe_text = open(self.path).read()

    def get_title(self, split_on="CRUST"):
        recipe = self.recipe_text
        self.title = recipe.split(split_on)[0].strip()

    def get_crust_filling(self, split_on="CRUST", and_on="FILLING"):
        crust_and_filling = self.recipe_text.split(split_on)[1].strip()
        crust, filling = crust_and_filling.split(and_on)
        self.crust = self.remmove_first_character(crust)
        self.filling = self.remmove_first_character(filling)

    def remmove_first_character(self, subject_string):
        return subject_string[1:].strip()

    def make_shopping_list(self):
        shopping_list = []
        for part in self.as_dict()['Parts']:
            for ingredient in part['ingredients']:
                instance = return_instance(ingredient)
                shopping_list.append(instance)
        return shopping_list

    def as_dict(self):
        return {"Title": self.title,
                "Parts": [
                    {"sub-title": "filling",
                     "ingredients": self.ingredients.get("filling"),
                     "steps": self.steps.get("filling")},
                    {"sub-title": "crust",
                        "ingredients": self.ingredients.get("crust"),
                        "steps": self.steps.get("crust")}]}


class Pie:

    has_top_crust = True
    has_fried = False
    bake_time = 4000  # ms

    def __init__(self, name, recipe_path=""):
        """construct the Pie class """
        self.name = name
        self.crust = None
        self.filling = None
        self.recipe_path = recipe_path
        self.recipe = None
        self.shopping_list = []
        self.unique_pie_id = str(uuid.uuid4())

    def process_recipe(self):
        "process_recipe() method to make shopping list/steps for the pie"
        self.recipe = Recipe(self, self.recipe_path)
        self.shopping_list = self.recipe.make_shopping_list()

    def get_filling(self):
        return self.filling


class ApplePie(Pie):
    has_fruit = True
    image_key = "A"


class CherryPie(Pie):
    has_fruit = True
    image_key = "B"


class RaseberryPie(Pie):
    has_fruit = True
    image_key = "C"


class Factory:
    def __init__(self):
        self.pies = {}
        self.oven_heat_time = 10000
        self.inventory = []
        self.pie_orders_qty = {}
        self.callbacks = defaultdict(list)
        self.known_callback_methods = ('bake', 'reload', 'oven', 'restock')

    def fill_pantry(self, pie, times=5):
        " Given a pie, duplicate items times 'times', adds to self.inventory"
        log.debug("restock")
        inventory = copy.copy(pie.shopping_list)
        for item in inventory:
            item.qty *= times
            self.inventory.append(item)

    def get_totals(self):
        out = {}
        for x in self.inventory:
            if x.item in out:
                out[x.item].qty += x.qty
            else:
                out[x.item] = copy.copy(x)
        return self.pretty_display_ingredients(out.values())

    @staticmethod
    def truncate(input, length=25):
        if len(input) > length:
            return input[:length] + "..."
        return input

    @staticmethod
    def humanize(frac):
        whole = " "
        part = "{}/{}".format(frac.numerator, frac.denominator)
        if frac.numerator > frac.denominator:
            whole = int(frac.numerator / frac.denominator)
            frac -= whole
            part = ""
            if frac.numerator != 0:
                part = "{}/{}".format(frac.numerator, frac.denominator)
        return "{} {}".format(whole, part)

    def pretty_display_ingredients(self, ingredients):
        out = defaultdict(list)
        for ingr in ingredients:
            as_str = "{} {} of {}".format(self.humanize(ingr.qty),
                                          ingr.unit,
                                          ingr.item)
            out[ingr.name].append(self.truncate(as_str))
        row_size = max(map(len, out.values()))
        for row in out.values():
            row += [""] * (row_size - len(row))
        table = prettytable.PrettyTable()
        for header, listings in out.items():
            table.add_column(header, listings)
        return table.get_string()

    def key_item_for_inventory(self):
        out = {}
        for ingr in self.inventory:
            out[ingr.item] = ingr
        log.debug(out)
        return out

    def add_pie(self, pie):
        self.pies[pie.unique_pie_id] = pie

        # calculate ingredients
        inventory_by_key = self.key_item_for_inventory()
        for ingrd in pie.shopping_list:
            if (inventory_by_key[ingrd.item].qty - ingrd.qty) < 0:
                raise Exception("out of {}".format(ingrd.item))
            inventory_by_key[ingrd.item].qty -= ingrd.qty

    def add_pie_order(self, pie, qty):
        pie.process_recipe()
        self.pie_orders_qty[pie.unique_pie_id] = qty
        self.add_pie(pie)

    def add_callback(self, method, func):
        if method not in self.known_callback_methods:
            raise Exception("unkown callback method: {}".format(method))
        self.callbacks[method].append(func)

    def run_factory(self):
        import jupy
        return jupy.run_flask_socket_app(factory=self)

    def run_factory_test(self):
        pass


def run_factory(test=False):
    factory = Factory()
    pie = ApplePie(name="Prototype Apple Pie", recipe_path="misc/ApplePie.txt")
    pie.process_recipe()
    factory.fill_pantry(pie, times=10)
    if test:
        factory.add_pie_order(pie, 3)
        log.debug("totals: ")
        log.debug(factory.get_totals())

    def echo_callback(callback_app, message):
        callback_app.logger.info("echo {}".format(message))

    for method in factory.known_callback_methods:
        factory.add_callback(method, echo_callback)

    names = ["Bob", "Sue", "Pap", "Karen", "Brian", "Greg"]

    def bake_callback(callback_app, message):
        callback_app.logger.info("bake callback")
        baketype = message['baketype']
        if baketype == 'apple':
            pie_type = ApplePie
        elif baketype == 'cherry':
            pie_type = CherryPie
        elif baketype == 'raseberry':
            pie_type = RaseberryPie
        else:
            raise Exception("unknown bake type {}".format(message['baketype']))
        pie = pie_type(name="{}'s {} Pie".format(random.choice(names), baketype.title()),
                       recipe_path="misc/ApplePie.txt")
        pie.process_recipe()
        try:
            callback_app.factory.add_pie(pie)
        except Exception as e:
            return dict(error=str(e))

        totals = callback_app.factory.get_totals()
        return dict(image_key=pie.image_key,
                    totals=totals,
                    name=pie.name,
                    unique_pie_id=pie.unique_pie_id)

    factory.add_callback("bake", bake_callback)

    def oven_callback(callback_app, message):
        callback_app.logger.info("message {}".format(message))
        pie = callback_app.factory.pies[message['unique_pie_id']]
        total_time = message['heat_time'] + callback_app.factory.oven_heat_time
        totals = callback_app.factory.get_totals()
        return dict(image_key=pie.image_key,
                    totals=totals,
                    oven_msg="Oven Heating",
                    name=pie.name,
                    bake_time=pie.bake_time,
                    total_time=total_time,
                    unique_pie_id=pie.unique_pie_id)

    factory.add_callback("oven", oven_callback)

    def restock_callback(callback_app, message):
        callback_app.logger.info("message {}".format(message))
        callback_app.factory.fill_pantry(pie, times=1)
        totals = callback_app.factory.get_totals()
        return dict(msg="restocked",
                    totals=totals)

    factory.add_callback("restock", restock_callback)

    if test:
        return factory.run_factory_test()
    else:
        return factory.run_factory()


def run_detached():
    import subprocess
    return subprocess.Popen([sys.executable, os.path.realpath(__file__)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True)


def stop_detached(process):
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)


base_class = object

try:
    import IPython
    import IPython.core.display
    base_class = IPython.core.display.HTML
except:
    print("Unexpected error:", sys.exc_info()[0])


def give_me_iframe(src, width="100%", height=525):
    frame_html = """<iframe id="jupy" scrolling="no" style="border:none;"
                    seamless="seamless"
                    src="{src}"
                    height="{height}" width="{width}">
                    </iframe>""".format(**locals())
    return frame_html


class JupyDisplay(base_class):
    """

    """

    def __init__(self, url, width="100%", height=525):
        self.resource = url
        self.embed_code = give_me_iframe(url, width=width, height=height)
        super(JupyDisplay, self).__init__(data=self.embed_code)

    def _repr_html_(self):
        return self.embed_code


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Complete pie factory')
    parser.add_argument(
        '--test', action="store_true", help='test the factory code',)
    args = parser.parse_args()
    test = False
    if args.test:
        log.info("running in test mode")
        test = True
    else:
        log.info("running in single server mode")
    run_factory(test=test)
