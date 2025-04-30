from enum import Enum
from os import listdir, mkdir
from os.path import isfile, isdir, join, split, splitext
import platform
import json

CORE_ASSETS_PATH = "./node_modules/core-pixi-webpack/lib/assets/"
GAME_ASSETS_PATH = "./assets"
DESTINATION_PATH = "./data"

print("PLATFORM RUNNING: ",platform.system())
if platform.system() == "Windows":
    CORE_ASSETS_PATH = ".\\node_modules\\core-pixi-webpack\\lib\\assets\\"
    GAME_ASSETS_PATH = ".\\assets"
    DESTINATION_PATH = ".\\data"

USE_DIRECTORIES = [
    CORE_ASSETS_PATH, 
    GAME_ASSETS_PATH
]

class AssetsType(Enum):
    ASSETS = 0
    FONTS = 1
    SOUNDS = 2
    SPINES = 3

ASSETS_CONFIG_MAP = {
    AssetsType.ASSETS: join(DESTINATION_PATH, "assets_config.json"), 
    AssetsType.FONTS: join(DESTINATION_PATH, "fonts_config.json"), 
    AssetsType.SOUNDS: join(DESTINATION_PATH, "sounds_config.json"), 
    AssetsType.SPINES: join(DESTINATION_PATH, "spines_config.json")
}

ASSETS_DIRECTORY_MAP = {
    AssetsType.ASSETS: ["brands", "sprite_sheets", "statics"], 
    AssetsType.FONTS: ["bitmap", "common", "json"], 
    AssetsType.SOUNDS: ["music", "sounds", "gamble_sounds"], 
    AssetsType.SPINES: ["spines"]
}

base_assets_template = {
    AssetsType.ASSETS: {
        "groups": {
            "preload": [],
            "initial": [],
            "lazy": []
        }
    },
    AssetsType.FONTS: {
        "groups": {
            "preload": [],
            "initial": [],
            "lazy": []
        }
    },
    AssetsType.SOUNDS: {
        "groups": {
            "preload": [],
            "initial": [],
            "lazy": []
        }
    },
    AssetsType.SPINES: {
        "groups": {
            "preload": [],
            "initial": [],
            "lazy": []
        }
    }
}

configured_assets = {}
sounds_added = {}
spines_added = {}

def get_json_subfile(json_file, keys = ["meta", "image"]):
    json_data = None

    with open(json_file, "r") as file:
        json_data = json.load(file)
    
    if json_data != None:
        if len(keys) == 1:
            return json_data.get(keys[0])
        else:
            data = get_json_subfile(json_file, keys[:len(keys) - 1])
            data = data.get(keys[len(keys) - 1])
            if type(data) == str:
                data = splitext(data)
            return data
    else:
        return ""

def get_group(phase):
    match phase:
        case "preload":
            return "preloader_group"
        case "initial":
            return "initial_group"
        case "lazy":
            return "" #TODO - defining the group's name for lazy assets loading

def get_extension_key_name(extension):
    match extension:
        case ".webp":
            return "image"
        case _:
            return extension[1:]

def set_config(asset_type, phase, template):
    file_name = template["name"]
    location = None
    if file_name in configured_assets:
        location = configured_assets[file_name]
        previous_asset_type = location["asset_type"]
        previous_phase = location["phase"]
        previous_index = location["index"]
        base_assets_template[previous_asset_type]["groups"][previous_phase][previous_index] = template
    else:
        location = {
            "asset_type": asset_type,
            "phase": phase,
            "index": len(base_assets_template[asset_type]["groups"][phase])
        }
        if asset_type == AssetsType.SPINES:
            if "isMultiAtlas" in template:
                for entry in base_assets_template[asset_type]["groups"][phase]:
                    configured_assets[entry["name"]]["index"] += 1
                base_assets_template[asset_type]["groups"][phase].insert(0, template)
                location["index"] = 0
            else:
                base_assets_template[asset_type]["groups"][phase].append(template)
        else:
            base_assets_template[asset_type]["groups"][phase].append(template)
        configured_assets[file_name] = location

def traverse_files(path, assets_path, phase, asset_type, directory):
    try:
        for entry in listdir(path):
            full_path = join(path, entry)
            if isdir(full_path):
                traverse_folders(path, assets_path, phase, asset_type)
            elif str(entry) != "git.keep" and isfile(full_path):
                file_splitted_name = splitext(entry)
                template = {}
                if platform.system() == "Windows":
                    template["path"] = (str(assets_path) + "\\").replace("\\", "/")
                else:
                    template["path"] = str(assets_path) + "/"
                template["name"] = file_splitted_name[0]
                if asset_type == AssetsType.SOUNDS or asset_type == AssetsType.SPINES:
                    template["ext"] = {
                        "atlas": ".atlas",
                        "image": ".webp",
                        "skeleton": ".json"
                    }
                else:
                    template["extension"] = file_splitted_name[1]
                template["group"] = ["" + str(get_group(phase))]
                #template["platform"] = ["desktop", "mobile"]
                #template["platform"] = ["mobile"]
                #template["platform"] = []
                match asset_type:
                    case AssetsType.ASSETS:
                        if directory == "statics":
                            #print(template)
                            set_config(asset_type, phase, template)
                        elif file_splitted_name[1] == ".json":
                            subfile = get_json_subfile(full_path)
                            template["imgName"] = subfile[0]
                            template["imgExtension"] = subfile[1]
                            #print(template)
                            set_config(asset_type, phase, template)
                    case AssetsType.FONTS:
                        if directory == "bitmap":
                            #TODO - support for bitmap fonts
                            #print(template)
                            #base_assets_template[asset_type]["groups"][phase].append(template)
                            if file_splitted_name[1] == '.fnt' or file_splitted_name[1] == '.ttf':
                                set_config(asset_type, phase, template)
                        else:
                            #print(template)
                            set_config(asset_type, phase, template)
                    case AssetsType.SOUNDS:
                        if file_splitted_name[0] in sounds_added:
                            base_assets_template[asset_type]["groups"][phase][sounds_added[file_splitted_name[0]]]["ext"][file_splitted_name[1][1:]] = file_splitted_name[1]
                            #print(base_assets_template[asset_type]["groups"][phase][sounds_added[file_splitted_name[0]]])
                        else:
                            template["ext"][file_splitted_name[1][1:]] = file_splitted_name[1]
                            set_config(asset_type, phase, template)
                            sounds_added[file_splitted_name[0]] = len(base_assets_template[asset_type]["groups"][phase]) - 1
                    case AssetsType.SPINES:
                        main_spine = "spineMain"
                        if main_spine in file_splitted_name[0]:
                            if main_spine == file_splitted_name[0]:
                                template["isMultiAtlas"] = True
                                set_config(asset_type, phase, template)
                        elif "main_" in file_splitted_name[0]:
                            template["atlasLink"] = main_spine
                            set_config(asset_type, phase, template)
                        else:
                            set_config(asset_type, phase, template)
                        #print(template, entry, file_splitted_name[0])
    except FileNotFoundError:
        print("ERROR: cannot find path '{0}'".format(path))

def traverse_folders(path, assets_path, phase, asset_type):
    directories = ASSETS_DIRECTORY_MAP[asset_type]
    try:
        for entry in listdir(path):
            sub_path = join(path, entry)
            sub_assets_path = join(assets_path, entry)
            if isdir(sub_path):
                if entry not in directories:
                    traverse_folders(sub_path, sub_assets_path, phase, asset_type)
                else:
                    traverse_files(sub_path, sub_assets_path, phase, asset_type, entry)
    except FileNotFoundError:
        print("ERROR: cannot find path '{0}'".format(path))

def generate_config():
    for path in USE_DIRECTORIES:
        for asset_type in base_assets_template:
            for group in base_assets_template[asset_type]:
                for phase in base_assets_template[asset_type][group]:
                    traverse_folders(join(path, phase), join(GAME_ASSETS_PATH, phase), phase, asset_type)

def save_to_file(asset_type):
    type_path = ASSETS_CONFIG_MAP[asset_type]
    config_data = base_assets_template[asset_type]
    if not isdir(DESTINATION_PATH):
        mkdir(DESTINATION_PATH)
    with open(type_path, "w") as file:
        json_data = json.dumps(config_data, indent = 4)
        file.write(json_data)

def save_config_data():
    for asset_type in ASSETS_CONFIG_MAP:
        save_to_file(asset_type)
    print("assets configuration files created!")

generate_config()
save_config_data()