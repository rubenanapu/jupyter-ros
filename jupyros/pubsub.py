import threading
import time
import ipywidgets as widgets
import sys
import rospy
import inspect

output_registry = {}
subscriber_registry = {}

def callback_active():
    return threading.currentThread().name in active_callbacks

class OutputRedirector:
    def __init__(self, original):
        self.original = original
    
    def write(self, msg):
        thread_name = threading.currentThread().name
        if thread_name != 'MainThread':
            output_registry[threading.currentThread().getName()].append_stdout(msg)
        else:
            self.original.write(msg)
            
    def flush(self):
        self.original.flush()

sys.stdout = OutputRedirector(sys.stdout)

def subscribe(topic, msg_type, callback):
    """
    Subscribes to a specific topic in another thread, but redirects output!
    
    @param topic The topic
    @param msg_type The message type
    @param callback The callback
    
    @return Jupyter output widget
    """

    if subscriber_registry.get(topic):
        raise Error("Already registerd...")

    out = widgets.Output(layout={'border': '1px solid black'})
    subscriber_registry[topic] = rospy.Subscriber(topic, msg_type, callback)
    output_registry[topic] = out

    btn_stop = widgets.Button(description="Stop")

    def stop_subscriber(x):
        subscriber_registry[topic].unregister()
        del output_registry[topic]

    btn_stop.on_click(stop_subscriber)

    btn_start = widgets.Button(description="Start")

    def start_subscriber(x):
        output_registry[topic] = out
        subscriber_registry[topic] = rospy.Subscriber(topic, msg_type, callback)

    btn_start.on_click(start_subscriber)

    btns = widgets.HBox((btn_stop, btn_start))
    vbox = widgets.VBox((btns, out))
    return vbox