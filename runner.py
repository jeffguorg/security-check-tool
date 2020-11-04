import time
import traceback

from native_os import NativeOS


def get_all_methods():
    # https://stackoverflow.com/questions/34439/finding-what-methods-a-python-object-has/20100900
    instance = NativeOS().instance()
    return [method_name for method_name in dir(instance)
            if callable(getattr(instance, method_name)) and not method_name.startswith('__')]


def run_instance_method(method_name, max_items=3):
    print(f'***************** {method_name} ***************** ')
    func = getattr(NativeOS().instance(), method_name)
    ts = time.time()
    generator = func()
    for i, item in enumerate(generator):
        if i == max_items:
            break
        print(item)
    te = time.time()
    cost_ms = (te - ts) * 1000
    return '%.2f ms' % cost_ms


def dump_results(methods, is_ok):
    if len(methods) == 0:
        return
    if is_ok:
        print("-------------------OK------------------")
    else:
        print("-----------------FAILED----------------")
    for name in methods:
        print(name)


def run_methods(selected_methods: list):
    obj_methods = get_all_methods()
    if selected_methods is None:
        selected_methods = obj_methods
    total_count = len(selected_methods)
    implement_methods = []
    failed_methods = []
    for i, method_name in enumerate(selected_methods):
        i += 1
        assert (method_name in obj_methods)
        try:
            spent_ms = run_instance_method(method_name)
            implement_methods.append((i, method_name, spent_ms))
        except Exception as ex:
            traceback.print_exc()
            failed_methods.append((i, method_name, ex))
    dump_results(failed_methods, False)
    dump_results(implement_methods, True)
    implement_count = len(implement_methods)
    print(f"{implement_count} of {total_count} has implemented {implement_count * 100 / total_count}%")
