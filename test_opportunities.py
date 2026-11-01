from tools.opportunity_search import (
    search_greenhouse,
    search_lever
)


def main():
    print("\nCAREER OPPORTUNITY DISCOVERY\n")

    provider = input(
        "Provider (greenhouse/lever): "
    ).strip().lower()

    company = input(
        "Company name: "
    ).strip()

    token = input(
        "Job board token/site: "
    ).strip()

    try:
        if provider == "greenhouse":
            jobs = search_greenhouse(
                token,
                company
            )

        elif provider == "lever":
            jobs = search_lever(
                token,
                company
            )

        else:
            print("Unsupported provider.")
            return

    except requests.RequestException as error:
        print(f"Could not retrieve jobs: {error}")
        return

    print(f"\nFound {len(jobs)} relevant positions\n")

    for job in jobs:
        print("Category:", job["category"])
        print("Company:", job["company"])
        print("Role:", job["title"])
        print("Location:", job["location"])
        print("URL:", job["url"])
        print("-" * 50)


if __name__ == "__main__":
    import requests
    main()