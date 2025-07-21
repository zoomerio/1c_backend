import configparser, os

config = configparser.ConfigParser()
config["LOGGER"] = {}
config["LOGGER"]["log_file"] = "backend.log"
config["LOGGER"]["log_level"] = "DEBUG"
config["KEYCLOAK"] = {}
config["KEYCLOAK"]["host"] = "http://localhost:8080"
config["KEYCLOAK"]["username"] = "admin"
config["KEYCLOAK"]["password"] = "password"
config["KEYCLOAK"]["realms"] = "EDIT_ME!!!"


def create_or_update_config_file(path):
    if not os.path.exists(path):
        with open(path, "w") as configfile:
            config.write(configfile)
    else:
        old_config = configparser.ConfigParser()
        old_config.read(path)
        for section in config.sections():
            if section not in old_config.sections():
                old_config.add_section(section)
            for option in config.options(section):
                if option not in old_config.options(section):
                    old_config.set(section, option, config.get(section, option))
        with open(path, "w") as configfile:
            old_config.write(configfile)

# TODO: DEPRECATED
# def find_user_by_patronymic(users, patronymic, except_ids=None):
#     if except_ids is None:
#         except_ids = []
#     for user in users:
#         if user.get("SECOND_NAME"):
#             if user.get("SECOND_NAME").lower() == patronymic.lower() and user.get("ID") not in except_ids:
#                 return user
#     return None

