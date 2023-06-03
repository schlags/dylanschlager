import argparse
import csv
import requests
import json

def finalize(horse_name):
    # Implementation for the 'finalize' option
    print(f"Finalizing the race for horse: {horse_name}")

    # Prepare the payload
    payload = {
        "horse_id": horse_name
    }

    # Send the POST request
    url = "https://6g125mlu01.execute-api.us-east-1.amazonaws.com/finalize"

    payload = json.dumps({
    "horse_id": f"{horse_name}"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Process the response
    if response.status_code == 200:
        data = response.json()
        print("Race finalized successfully!")
        print("Winning Horse:", data["winning_horse"])
        print("Players Paid:")
        for player in data["players_paid"]:
            print(f"  - {player['player_id']} won {player['winnings']}")
        # print("Bets:", data["bets"])
    else:
        print("Failed to finalize the race.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

def newrace(csv_file):
    # Implementation for the 'newrace' option
    print(f"Creating a new race with CSV file: {csv_file}")

    # Read and process the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            payload = json.dumps({
                "horse_id": row["horse_id"],
                "race_name": row["race_name"],
                "odds": row["odds"]
            })

            # Send the POST request for each payload
            url = "https://6g125mlu01.execute-api.us-east-1.amazonaws.com/races"  # Replace with your API endpoint
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            # Process the response
            if response.status_code == 201:
                print(f"Race created successfully: {payload}")
            else:
                print(f"Failed to create the race: {payload}")

def main():
    parser = argparse.ArgumentParser(description="Race Management CLI Tool")

    # Add options for 'finalize' and 'newrace'
    parser.add_argument('command', choices=['finalize', 'newrace'], help="Command to execute")
    parser.add_argument('horse_name', nargs='?', help="Horse name (only for 'finalize')")
    parser.add_argument('csv_file', nargs='?', help="Path to the CSV file (only for 'newrace')")
    
    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == 'finalize':
        if args.horse_name is None:
            print("Error: 'finalize' command requires a horse name.")
        else:
            finalize(args.horse_name)
    elif args.command == 'newrace':
        if args.csv_file is None:
            print("Error: 'newrace' command requires a CSV file path.")
        else:
            newrace(args.csv_file)

if __name__ == "__main__":
    main()
