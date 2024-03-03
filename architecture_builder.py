class Module:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("Module",),
                "name": (
                    "STRING",
                    {
                        "multiline": False,
                    },
                ),
                "repeats": (
                    "INT",
                    {
                        "min": 1,
                        "max": 999999999,
                        "default": 1,
                    },
                ),
                "arguments": (
                    "STRING",
                    {
                        "multiline": True,
                    },
                ),
                "notes": (
                    "STRING",
                    {
                        "multiline": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("Module",)
    RETURN_NAMES = ("output",)
    CATEGORY = "NNArch"


class Group:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input 1": ("Module",),
                "input 2": ("Module",),
            },
        }

    RETURN_TYPES = ("Module",)
    RETURN_NAMES = ("output",)
    CATEGORY = "NNArch"


NODE_CLASS_MAPPINGS = {
    "NNModule": Module,
    "NNGroup": Group,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NNModule": "Module",
    "NNGroup": "Group",
}
