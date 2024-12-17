import argparse

def main():
    parser = argparse.ArgumentParser(description="Process an Excel report.")
    parser.add_argument("--report", type=str, required=True, help="Path to the Excel file")
    args = parser.parse_args()

    print(f"Processing Excel report at: {args.report}")

if __name__ == "__main__":
    main()
