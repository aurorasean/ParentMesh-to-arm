import bpy.utils.previews
import os

preview_collections = {}

preview_collections['default'] = {}

def register():
    image_dir = os.path.join(os.path.dirname(__file__), "images")
    # get all child directories in the images directory
    if os.path.exists(image_dir):
        child_dirs = [
            d
            for d in os.listdir(image_dir)
            if os.path.isdir(os.path.join(image_dir, d))
        ]
        for child_dir in child_dirs:
            child_path = os.path.join(image_dir, child_dir)
            child_dir_name = child_dir.replace(image_dir, "").strip(os.sep)
            if os.path.exists(child_path):#
                
                preview_collections[child_dir_name] = {}
                files = [
                    f
                    for f in os.listdir(child_path)
                    if os.path.isfile(os.path.join(child_path, f))
                ]
                for file_name in files:
                    icon_path = os.path.join(child_path, file_name)
                    cleanColourName = file_name.split("-")[0]
                    pcoll = bpy.utils.previews.new()
                    colourValues = file_name.split("-")[1:]  # remove the first one
                    colourValues[-1] = os.path.splitext(colourValues[-1])[
                        0
                    ]  # remove the extension from the last element
                    colourValues = [float(v) for v in colourValues]
                    colour_tuple = tuple(colourValues)
                    pcoll.colour = colour_tuple

                    # load a preview thumbnail of a file and store in the previews collection
                    pcoll.load(cleanColourName, icon_path, "IMAGE")
                    # print(dir(pcoll))
                    preview_collections[child_dir_name][cleanColourName] = pcoll

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder

def get_libraries():
    return [(lib, lib, "") for lib in preview_collections] 
def get_colours(library="default"):
    return preview_collections[library]


def unregister():

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
