from services.user import fetch_user, delete_user


def main():
    user = fetch_user(1)
    print(user)

    delete_user(1)


if __name__ == "__main__":
    main()