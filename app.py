from scrapper.run import run_scrapper
from neo4j.run import run_refresh_database


def main():
    while True:
        print("\nOptions:")
        print("1. Run scraper")
        print("2. Run Neo4j script")
        print("Ctrl+C to exit")

        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            run_scrapper()
        elif choice == "2":
            run_refresh_database()
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the script.")
