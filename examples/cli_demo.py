import os
import sys

# Add parent directory to path to allow importing agentic_sports without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentic_sports import Simulator, Agent

# You must set this in your environment or replace the string below
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("Error: Please set GEMINI_API_KEY environment variable.")
    print("Example: export GEMINI_API_KEY='your_api_key_here'")
    sys.exit(1)

def print_event(event: dict):
    """Callback function to print simulation events to the console."""
    event_type = event.get("type")
    
    if event_type == "system":
        print(f"\n[{event.get('home_score')}-{event.get('away_score')}] {event.get('text')}\n")
    elif event_type == "play":
        print(f"[{event.get('home_score')}-{event.get('away_score')}] {event.get('text')}")
    elif event_type == "final":
        print(f"\n=== {event.get('text')} ===\n")

def main():
    print("Initializing Agentic Sports Simulation Demo...")

    # Create dummy agents (Normally you load from markdown files)
    lebron = Agent(name="LeBron James", shooting=85, defense=88, passing=90, speed=85, stamina=95, 
                   memory="Experienced veteran, makes smart reads.", skills="Elite driver and passer.")
    curry = Agent(name="Stephen Curry", shooting=99, defense=70, passing=85, speed=88, stamina=92, 
                  memory="Greatest shooter of all time.", skills="Limitless range and off-ball movement.")
    
    # Initialize the Simulator with our console print callback
    # We set delay to 0 for a fast demo
    sim = Simulator(api_key=API_KEY, model="gemini-2.5-flash", on_event=print_event)
    
    print("\nStarting an isolation 1v1 match...")
    # Run a short 1-quarter match with 4 possessions
    sim.run_match(
        home_team=[lebron], 
        away_team=[curry], 
        quarters=1, 
        quarter_possessions=4,
        delay_between_plays=0
    )

if __name__ == "__main__":
    main()
