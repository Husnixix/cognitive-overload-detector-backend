from controllers.session_controller import SessionController
import time

def main():
    controller = SessionController()

    print("Starting session...")
    result = controller.start_session()
    print(result)

    print("Press Ctrl+C to stop session...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping session...")
        result = controller.stop_session()
        print(result)

        print("Retrieving session data:")
        data = controller.get_session_data()
        print(data)

if __name__ == "__main__":
    main()
