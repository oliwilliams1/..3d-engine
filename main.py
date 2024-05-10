import time
import threading
import config

physics_ready = False
number_of_objects = None
physics_objects = None
running = True
physics_lock = threading.Lock()  # Add a lock for synchronization
physics_tps = 1 / 12.5
dev_ui_tps = 1 / 10
previous_physics_objects = None
dev_ui_wants_update = False
dev_ui_objects = None

def run_graphics_engine():
    global running, dev_ui_wants_update, dev_ui_objects, previous_physics_objects
    while not physics_ready and running:
        time.sleep(0.01)
        
    import graphics_engine
    app = graphics_engine.GraphicsEngine()
    import c_modules.interpolate_objects as interpolate_objects

    while running:
        with physics_lock:
            temp_prev_obj = previous_physics_objects
            temp_obj = physics_objects

        local_objects = interpolate_objects.interpolate_physics_objects(temp_prev_obj, temp_obj, time.monotonic())
        app.update(local_objects)
        app.run()
        if dev_ui_wants_update:
            temp_dev_objects = app.retrieve_objects()
            dev_ui_objects = temp_dev_objects

def run_physics_engine():
    import physics
    global physics_ready, physics_objects, number_of_objects, running, previous_physics_objects

    while running:
        start_time = time.monotonic()
        physics.main()
        temp_physics_objects = []

        for obj in physics.objects:
            position = obj.position
            temp_physics_objects.append([position[0], position[1], position[2]])

        with physics_lock:
            previous_physics_objects = physics_objects
            physics_objects = [temp_physics_objects, time.monotonic()]

        physics_ready = True

        elapsed_time = time.monotonic() - start_time
        sleep_time = max(0, physics_tps - elapsed_time)
        time.sleep(sleep_time)

    physics.destroy()

def dev_window():
    global running, dev_ui_wants_update, dev_ui_objects
    import dev_main
    dev_ui = dev_main.DevUI()
    
    while running:
        start_time = time.monotonic()

        dev_ui.update()

        elapsed_time = time.monotonic() - start_time
        sleep_time = max(0, dev_ui_tps - elapsed_time)
        time.sleep(sleep_time)
        
        dev_ui_wants_update = dev_ui.dev_ui_wants_update

        if dev_ui_wants_update:
            dev_ui.objects = dev_ui_objects
            if type(dev_ui_objects) == list :
                dev_ui_wants_update = False
                dev_ui.dev_ui_wants_update = False
                dev_ui.valid_objects = True

    dev_ui.destroy()

if __name__ == '__main__':
    raise SyntaxError("using wrong file, use graphics_engine.py")
    config_app = config.Config()
    is_dev = config_app.retrieveConfig('DEV_MODE')
    graphics_engine_thread = threading.Thread(target=run_graphics_engine)
    physics_engine_thread = threading.Thread(target=run_physics_engine)

    if is_dev:
        dev_window_thread = threading.Thread(target=dev_window)

    physics_engine_thread.start()
    graphics_engine_thread.start()
    if is_dev:
        dev_window_thread.start()

    while running:
        running = graphics_engine_thread.is_alive()
        time.sleep(0.1)