
from datetime import datetime
import random
from pie_logger import get_logger
log = get_logger()


#  socket.emit('callback', {action: 'oven', unique_pie_id: pie.unique_pie_id, heat_time: game.time.now})
#  socket.emit('callback', {action: 'bake', baketype: 'apple'});
#  socket.emit('callback', {action: 'bake', baketype: 'cherry'});
#  socket.emit('callback', {action: 'bake', baketype: 'raseberry'});
#  socket.emit('callback', {action: 'restock'});


class MockApp:
    def __init__(self, belt):
        self.logger = log
        self.belt = belt


def get_random_pie():
    return random.choice(["apple", "cherry", "raseberry"])


def simulate(belt, count, delay=5):

    callback_app = MockApp(belt)

    for callback in belt.callbacks.get("restock", []):
        callback(callback_app, {})

    for n in range(count):
        log.debug("testing bake callback")
        for callback in belt.callbacks.get('bake', []):
            bake_out = callback(callback_app, dict(baketype=get_random_pie()))
            if bake_out:
                for callback in belt.callbacks.get('oven', []):
                    callback(callback_app, dict(
                        unique_pie_id=bake_out.get('unique_pie_id'),
                        heat_time=4))
    log.debug("\n"+belt.get_totals())
