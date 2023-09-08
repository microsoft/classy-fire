try:
    import classy_fire
    print("Sanity check passed: 'classy_fire' module imported successfully.")
except ImportError as e:
    print(f"Sanity check failed: Unable to import 'classy_fire': {e}")
    exit(1)