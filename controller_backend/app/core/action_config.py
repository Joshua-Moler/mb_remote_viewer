import os
import uuid
import yaml
import json
import random
import pathlib
from random import choice
from app.core.Utils import *
from app.core.Valves import *
from app.core.Pumps import *
from app.core.Pressures import *
from app.core.Turbos import *
from app.core.States import *
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_rdb
# from app.db.crud import (
#     save_logs
# )
from app.core import config

import logging

rdb = r.connect(url=config.RETHINK_DB_URI).repl()


error_state = False
gaction_name = 'cool_down'


def get_random_bool():
    return random.choice([True, False])


class Dict2Class(object):
    def __init__(self, my_dict):
        self.run_id = None  # process id
        self.fn = None  # fn
        self.arg = None  # argument
        self.parallel = None    # is parallel function or not
        self.onfail = False  # what to do on fail
        self.formula = None  # formula
        self.condition = None   # formula condition
        self.content = None
        self.user = None
        self.state = None  # global state
        self.results = None  # result outcome
        self.status = None  # result status / true / false
        self.created_at = None

        for key in my_dict:
            v = my_dict[key]
            if isinstance(v, str) and v.lower() == 'none':
                v = None
            setattr(self, key, v)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def read_yml():
    # print (os.path.join(pathlib.Path().resolve(), 'maybell.yaml'))
    # print (os.path.join(pathlib.Path(__file__).parent.resolve(), '../../'))
    with open(os.path.join(pathlib.Path().resolve(), 'maybell.yaml'), "r") as stream:
        try:
            _yaml = yaml.safe_load(stream)
            return _yaml
        except yaml.YAMLError as exc:
            print(exc)


# (bool, obj)
# #1 - False  - its a fail
# #2 - desired return value


def check_error(r=False, o=None, f=None):
    if o and o.onfail and not r:
        # write to DB
        print(f"Setting ERROR: True {f}")
        return True
    return False

# add decorators to all actionable functions


@dec
def close_valve(v=None, o=None, db=None):
    (result, returned_data) = valve_close(v)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def open_valve(v=None, o=None, db=None):
    (result, returned_data) = valve_open(v)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def toggle_valve(v=None, o=None, db=None):
    (result, returned_data) = valve_toggle(v)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def start_pump(p=None, o=None, db=None):
    (result, returned_data) = pump_start(p)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def start_turbo(t=None, o=None, db=None):
    (result, returned_data) = turbo_start(t)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def state_check(a=None, o=None, db=None):
    (result, returned_data) = check_state(a)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def pressure_check(a=None, o=None, db=None):
    (result, returned_data) = check_pressure(a)
    return (result, returned_data, o, inspect.stack()[0][3])


@dec
def state_change(a: str = None, o=None, db=None):
    (result, returned_data) = change_state(a)
    return (result, returned_data, o, inspect.stack()[0][3])


'''
The code is trying to execute the function exec_func with two arguments, o and c. The code is checking for errors in the function before executing it.
If an error occurs, then the code skips execution of that line of code by printing "Skipping {o.fn} due to error_state: {error_state}" and returns None as a result.
Otherwise, if there are no errors, then the code executes eval on fn which will return either a string or an Exception object depending on whether or not there was an error condition in fn .
If there was no error condition in fn , then it will print "SUCCESS: {o.fn} check condition succeeded" and continue execution at the next line of code after try/except block (which prints out ERROR: {o.fn} check condition failed).
If there was an exception thrown during evaluation of fn , then it will print "ERROR: {o.fn} check condition failed" followed by a detailed explanation about what went wrong printed out to audit logs using fprintf() .
The code attempts to check if the function fn exists and if it does, then it will call the function with the argument a.
If there is no such function in the system, then an error state will be set and that particular execution of this snippet will be skipped.
If there is a function fn in the system, then we will create a new one using f'{f}("{a}", o)' where f'{f}()' would be used to call that particular function with o as its argument.
'''


def exec_func(o):
    global error_state
    global rdb
    if error_state:
        print(f"Skipping {o.fn} due to error_state: {error_state}")
        return None
    if o.fn:
        f = o.fn
        a = o.arg
        fn = f'{f}(None, o)'
        if a:
            fn = f'{f}("{a}", o)'
        try:
            result = eval(fn)

            if o.formula:
                fn = f"{result[1]} {o.formula}"
                eresult = eval(fn)
                # write to audit_logs
                if not eresult:
                    error_state = True
                    print(f"ERROR: {o.fn} check condition failed {fn}")
                    # return None
                    # raise Exception ()
                else:
                    print(f"SUCCESS: {o.fn} check condition succeeded {fn}")
                print(eresult)
            else:
                error_state = check_error(result[0], result[2])
                pass

            _o = result[2]
            _o.status = result[0]
            _o.results = result[1]

            write_data(rdb, config.LOGS, json.loads(_o.toJSON()))

            # write to auditlogs
        except Exception as e:
            raise Exception(f"Error occurred {e} {o.toJSON()}")


'''
The code begins by checking if the variable parallel_mode is set to True.
If it is, then the code sets up a for loop that iterates through all of the keys in perform_action.
For each key, we create an instance of Dict2Class and call exec_func on it with current user as its argument.
If parallel mode is not enabled, then we check if there's a value in perform_action[k]['parallel'] and if so, whether or not it's equal to 'start'.
If so, then we enable parallel mode and print out "PARALLEL: Enabling Parallel".
Otherwise, we disable parallel mode and print out "PARALLEL: Disabling Parallel".
The code is a snippet from the program that will be used to create a new class of objects.
The snippet is meant to demonstrate how to use the Dict2Class function in order to create classes of objects with different attributes and behaviors, such as 'if' and 'parallel'.
The code starts by creating an action_name variable that will hold the name of each individual object created in this code.
It then creates an empty dictionary called _yml which will hold all of the information about each object created in this code.
Next, it creates a list called perform_action which holds all of the actions available for this program.
Each key in perform_action corresponds with one action and each value corresponds with what
'''


def perform_actions(_yml, action_name, perform_action, current_user, parallel_mode, run_id=str(uuid.uuid4())):
    global error_state
    print(_yml[action_name]['description'])
    write_data(rdb, config.EVENTS, {'run_id': run_id, 'event_type': _yml[action_name]['description'],
               'start': None, 'end': None, 'started_by': current_user.email, 'temperature': None})

    if 'parallel' in perform_action:
        parallel_mode = True

    for k in perform_action.keys():

        actionClass = Dict2Class(perform_action[k])
        actionClass.user = current_user.email
        actionClass.run_id = run_id

        if k == 'if':
            exec_func(actionClass)
        else:
            exec_func(actionClass)

        if parallel_mode:
            _o = Dict2Class(_yml[action_name]['parallel'])
            _o.run_id = run_id
            _o.user = current_user.email
            exec_func(_o)

        if error_state:
            print(f"Breaking logic due to error: {error_state}")
            break

        # if 'parallel' mode enabled
        if 'parallel' in perform_action[k]:
            if parallel_mode and perform_action[k]['parallel'] == 'end':
                parallel_mode = False
                # print (f"PARALLEL:\tDisabling Parallel")
            elif not parallel_mode and perform_action[k]['parallel'] == 'start':
                parallel_mode = True
                # print (f"PARALLEL:\tEnabling Parallel")
    update_data(rdb, config.EVENTS, {
                'end': r.time(), 'temperature': None}, {'run_id': run_id})


'''
The code starts by declaring a variable called action_name.
This is the name of the action that we want to execute, and it will be used in later code.
The current_user variable is set to None because this function doesn't need any input from the user.
The next line of code declares a new variable called perform_action which will hold an object with actions for performing this particular action.
It also sets parallel_mode to False because there are no other actions to perform after executing this one.
Next, _yml is read into memory using read_yml().
If the action being executed has been defined in _yml then it's stored in perform_action as an object with 'actions'.
'''


def execute_action(action_name, current_user):
    create_table(config.LOGS, rdb)
    create_table(config.EVENTS, rdb)
    run_id = str(uuid.uuid4())
    gaction_name = action_name
    message = None
    global error_state
    parallel_mode = False
    _yml = read_yml()
    if action_name in _yml:
        perform_action = _yml[action_name]['actions']
        perform_actions(_yml, action_name, perform_action,
                        current_user, parallel_mode, run_id)

        message = f"Ok"
    else:
        message = f"Unknown {action_name}"

    return {'error_state': error_state, 'status': message, 'run_id': run_id}


if __name__ == '__main__':

    execute_action('pump_down', 'system')
    # # print ('hello')
    # with open("../../maybell.yaml", "r") as stream:
    #     try:
    #         _yaml = yaml.safe_load(stream)
    #         pump_down = _yaml['pump_down']['actions']
    #         for k in pump_down.keys():
    #             if k == 'if':
    #                 # exec_func(pump_down[k])
    #                 f = pump_down[k]['fn']
    #                 a = str(pump_down[k]['arg'])
    #                 fn = f'{f}("{a}")'
    #                 eval(fn)
    #             else:
    #                 exec_func(pump_down[k])
    #     except yaml.YAMLError as exc:
    #         print(exc)
