import sys
import os
import argparse

sys.path.append(os.path.abspath("src"))

from src.core.request import Request, RequestConfig
from src.core.satellite import Satellite, SatelliteConfig
from src.solver.scheduler import SatelliteScheduler


def run_sample_demo():
    """Run a sample demo with predefined satellite and requests"""
    satellite = Satellite(
        SatelliteConfig(
            MU=398600.4418,
            A=7000,
            EC=0.01,
            IC=45,
            OMEGA=60,
            W=30,
            R=6371,
            NUM_FRAMES=1000,
            memory_capacity_gb=10,
            image_size_per_km2_gb=0.15,
            image_duration_per_km2_sec=3.5,
            max_photo_duration_s=120,
            recalibration_time_s=30,
            speed_kms_per_s=50,
        )
    )

    requests = [
        Request(RequestConfig("New-York", (40.730610, -73.935242), 3, 6, (500, 1200))),
        Request(RequestConfig("Los-Angeles", (34.052235, -118.243683), 5, 8, (600, 1300))),
        Request(RequestConfig("Chicago", (41.878113, -87.629799), 2, 4, (700, 1400))),
        Request(
            RequestConfig("San-Francisco", (37.774929, -122.419416), 4, 5, (800, 1500))
        ),
        Request(RequestConfig("Miami", (25.761680, -80.191790), 3, 7, (400, 1100))),
        Request(RequestConfig("Seattle", (47.608013, -122.335167), 4, 6, (900, 1600))),
        Request(RequestConfig("Houston", (29.760427, -95.369803), 2, 5, (600, 1300))),
        Request(RequestConfig("Boston", (42.360081, -71.058880), 3, 4, (450, 1150))),
    ]

    scheduler = SatelliteScheduler(satellite, requests)
    status, results = scheduler.solve()
    scheduler.print_solution(status, results)


def run_llm_demo():
    """Run the interactive LLM-based demo"""
    try:
        from src.llm.pipeline import cli
        # Save original args
        original_argv = sys.argv.copy()
        # Clear sys.argv to prevent Click from processing main.py's arguments
        sys.argv = [sys.argv[0]]
        try:
            cli()
        finally:
            # Restore original args
            sys.argv = original_argv
    except ImportError as e:
        print(f"Error importing LLM pipeline: {e}")
        print("Make sure you have all required dependencies installed.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Satellite Capture Scheduler")
    parser.add_argument(
        "mode", 
        choices=["sample", "llm"],
        help="Mode to run: 'sample' for predefined demo or 'llm' for interactive LLM mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == "sample":
        print("Running sample demo with predefined satellite and requests...")
        run_sample_demo()
    elif args.mode == "llm":
        print("Starting interactive LLM-based demo...")
        run_llm_demo()


if __name__ == "__main__":
    main()
